from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str="student"

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str

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

class EnrollmentCreate(BaseModel):
    course_id:int

