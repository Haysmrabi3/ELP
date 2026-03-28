import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# بيشوف لو في رابط من ريلوي يستخدمه، لو مفيش يستخدم بتاع جهازك (Local)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # تعديل بسيط لأن ريلوي بيبعت الرابط بـ postgres:// و SQLAlchemy عايزاه postgresql://
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # ده الرابط بتاع الجهاز عندي ي هيثم 
    DATABASE_URL = "postgresql://postgres:Yassin%402007@localhost:5432/mydb"

engine = create_engine(DATABASE_URL)
 