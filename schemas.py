from pydantic import BaseModel, EmailStr
from typing import Optional, List

class UserCreate(BaseModel):
    username: str
    email: EmailStr # لضمان صحة صيغة الإيميل وتجنب خطأ 500
    password: str
    role: str = "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    role: str
    
class CourseCreate(BaseModel):
    title: str
    instructor: str
    rating: float
    reviews: int
    category: str
    price_type: str
    popular: int
    date: str
    image: str
    description: Optional[str] = None

class CourseOut(CourseCreate):
    id: int
    
class EnrollmentCreate(BaseModel):
    course_id: int