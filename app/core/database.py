import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ดึงค่าจาก Environment Variable หรือใช้ SQLite เป็น Default
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_CKNOAdgIk32E@ep-plain-cake-ao1z9qnt.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")

# ตั้งค่า connection args ตามชนิดของ Database
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency สำหรับใช้ใน FastAPI Routes (เหมือนการฉีด DbContext ใน C#)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()