from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ถ้าจะเปลี่ยนไปใช้ Database อื่น แค่เปลี่ยน URL ตรงนี้ครับ
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/hrm_pro.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
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