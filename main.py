from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from database import SessionLocal, engine
import models, schemas
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

# =========================
# ⚙️ إعدادات
# =========================

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 👇 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "my_super_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# =========================
# 🏠 ROOT
# =========================

@app.get("/")
def root():
    return {"message": "API is running 🚀"}

# =========================
# 🗄️ DB
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# 🔐 Password (FIX النهائي)
# =========================

def get_password_hash(password: str):
    password_bytes = password.encode("utf-8")[:72]  # 👈 الحل
    return pwd_context.hash(password_bytes)


def verify_password(plain_password: str, hashed_password: str):
    plain_bytes = plain_password.encode("utf-8")[:72]  # 👈 الحل
    return pwd_context.verify(plain_bytes, hashed_password)

# =========================
# 🔑 JWT
# =========================

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")

        if user_email is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(models.User).filter(
            models.User.email == user_email
        ).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_instructor(user: models.User = Depends(get_current_user)):
    if user.role != "instructor":
        raise HTTPException(status_code=403, detail="Only instructors allowed")
    return user

# =========================
# 🔐 AUTH
# =========================

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(
        (models.User.email == user.email) |
        (models.User.username == user.username)
    ).first()

    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        hashed_password = get_password_hash(user.password)

        new_user = models.User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {
            "message": "User created successfully",
            "user_id": new_user.id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong password")

    access_token = create_access_token(data={"sub": db_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# =========================
# 🎓 COURSES
# =========================

@app.post("/courses")
def create_course(
    course: schemas.CourseCreate,
    db: Session = Depends(get_db),
    instructor: models.User = Depends(require_instructor)
):
    new_course = models.Course(**course.dict())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@app.get("/courses", response_model=list[schemas.CourseOut])
def get_courses(
    db: Session = Depends(get_db),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    level: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    query = db.query(models.Course)

    if min_price is not None:
        query = query.filter(models.Course.price >= min_price)

    if max_price is not None:
        query = query.filter(models.Course.price <= max_price)

    if level:
        query = query.filter(models.Course.level == level)

    if search:
        query = query.filter(models.Course.title.contains(search))

    return query.all()


@app.get("/courses/{name}")
def search_course(name: str, db: Session = Depends(get_db)):
    courses = db.query(models.Course).filter(
        models.Course.title.ilike(f"%{name}%")
    ).all()

    if not courses:
        raise HTTPException(status_code=404, detail="No courses found")

    return courses


@app.delete("/courses")
def delete_course(
    name: str,
    price: float,
    db: Session = Depends(get_db),
    instructor: models.User = Depends(require_instructor)
):
    courses = db.query(models.Course).filter(
        models.Course.title.ilike(f"%{name}%"),
        models.Course.price == price,
        models.Course.is_deleted == False
    ).all()

    if not courses:
        raise HTTPException(status_code=404, detail="No courses found")

    for course in courses:
        db.delete(course)

    db.commit()

    return {"message": "Deleted successfully"}


@app.post("/enroll")
def enroll_course(
    data: schemas.EnrollmentCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):

    course = db.query(models.Course).filter(
        models.Course.id == data.course_id,
        models.Course.is_deleted == False
    ).first()

    if not course:
        raise HTTPException(404, "Course not found")

    existing = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == user.id,
        models.Enrollment.course_id == data.course_id
    ).first()

    if existing:
        raise HTTPException(400, "Already enrolled")

    enrollment = models.Enrollment(
        user_id=user.id,
        course_id=data.course_id
    )

    db.add(enrollment)
    db.commit()

    return {"message": "Enrolled successfully"}


@app.get("/my-courses")
def my_courses(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    enrollments = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == user.id
    ).all()

    courses = [en.course for en in enrollments if not en.course.is_deleted]

    return courses


@app.delete("/unenroll/{course_id}")
def unenroll(
    course_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    enrollment = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == user.id,
        models.Enrollment.course_id == course_id
    ).first()

    if not enrollment:
        raise HTTPException(404, "Not enrolled")

    db.delete(enrollment)
    db.commit()

    return {"message": "Unenrolled"}