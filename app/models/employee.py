from sqlalchemy import Column, Integer, String, Date, LargeBinary, ForeignKey, Enum, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
import enum
from datetime import datetime
from app.core.database import Base

class AttachmentCategory(enum.Enum):
    PROFILE = "profile"        # รูปโปรไฟล์
    CONTRACT = "contract"      # สัญญาจ้าง/ใบสมัคร
    MEDICAL = "medical"       # ใบรับรองแพทย์
    IDENTIFICATION = "id_card" # บัตรประชาชน/ทะเบียนบ้าน
    OTHERS = "others"          # เอกสารอื่นๆ

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(20), unique=True, index=True, nullable=False)
    
    first_name = Column(String(100), index=True, nullable=False)
    last_name = Column(String(100), index=True, nullable=False)
    
    email = Column(String(100), unique=True, index=True)
    join_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True) 
    base_salary = Column(Integer, default=15000)
    
    # 🔗 เชื่อมกับ User (ฝั่ง Employee เป็นคนถือ user_id)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("UserTable", back_populates="employee")
    
    # 📂 เอกสารแนบ
    attachments = relationship("Attachment", back_populates="employee", cascade="all, delete-orphan")

    # 🌳 สายบังคับบัญชา (Org Chart)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    subordinates = relationship("Employee", backref=backref("manager", remote_side=[id]))

class Attachment(Base):
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"))
    category = Column(Enum(AttachmentCategory), nullable=False)
    
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(100)) 
    file_data = Column(LargeBinary, nullable=False) 
    
    uploaded_at = Column(DateTime, default=datetime.now)
    
    employee = relationship("Employee", back_populates="attachments")