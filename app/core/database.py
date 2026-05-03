import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. ดึง URL จาก Environment Variable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_CKNOAdgIk32E@ep-plain-cake-ao1z9qnt.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")

# 2. แก้ไข Protocol สำหรับ SQLAlchemy 2.0 (ถ้าเป็น postgres:// ให้เปลี่ยนเป็น postgresql://)
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. สร้าง Engine พร้อมระบบกันท่อหลุด
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency สำหรับดึง DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()