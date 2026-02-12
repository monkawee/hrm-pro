from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    MANAGER = "manager"
    HR = "hr_officer"
    TOP_MANAGER = "top_manager"

class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String) # ในระบบจริงต้องเก็บเป็น Hash นะครับ
    full_name = Column(String)
    role = Column(SQLEnum(UserRole))
    is_active = Column(Boolean, default=True)