from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Date, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import Base

class TrainingStatus(enum.Enum):
    ENROLLED = "enrolled"
    COMPLETED = "completed"

class TrainingCourse(Base):
    __tablename__ = "training_courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    iso_code = Column(String(50), nullable=True) # ISO compliance code
    trainer = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    
    records = relationship("TrainingRecord", back_populates="course")

class TrainingRecord(Base):
    __tablename__ = "training_records"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("training_courses.id"), nullable=False)
    
    enrollment_date = Column(Date, default=datetime.now().date)
    completion_date = Column(Date, nullable=True)
    certificate_expiry_date = Column(Date, nullable=True)
    
    status = Column(Enum(TrainingStatus), default=TrainingStatus.ENROLLED)
    
    employee = relationship("Employee", backref="training_records")
    course = relationship("TrainingCourse", back_populates="records")
