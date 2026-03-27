from pydantic import BaseModel, constr, EmailStr

# =========================
# 👤 USER
# =========================

class UserCreate(BaseModel):
    username: str
    email: EmailStr  # 👈 يتحقق إنه email صح
    password: constr(min_length=6, max_length=72)  # 👈 حل مشكلة bcrypt + أمان أفضل
    role: str = "student"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # 👈 مهم مع SQLAlchemy


# =========================
# 🎓 COURSES
# =========================

class CourseCreate(BaseModel):
    title: str
    description: str
    price: int
    level: str


class CourseOut(BaseModel):
    id: int
    title: str
    description: str
    price: int
    level: str

    class Config:
        from_attributes = True


# =========================
# 📚 ENROLLMENT
# =========================

class EnrollmentCreate(BaseModel):
    course_id: int