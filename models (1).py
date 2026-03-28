from sqlalchemy import Column, Integer, String, Float
from database import Base
from sqlalchemy import Boolean

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role=Column(String, default=False)



class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    instructor = Column(String) 
    rating = Column(Float, default=0.0) 
    reviews = Column(Integer, default=0) 
    category = Column(String) 
    price_type = Column(String) 
    popular = Column(Integer, default=0) 
    date = Column(String) 
    image = Column(String) 
    description = Column(String)
    is_deleted = Column(Boolean, default=False)

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))

    user = relationship("User")
    course = relationship("Course")