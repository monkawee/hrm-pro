from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Date, Time, DateTime, Float, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import Base

class AttendanceStatus(enum.Enum):
    PRESENT = "present"
    LATE = "late"
    ABSENT = "absent"
    HALF_DAY = "half_day"

class Shift(Base):
    __tablename__ = "shifts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False) # e.g. "กะเช้า (09:00 - 18:00)"
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    late_grace_period = Column(Integer, default=15) # นาทีที่อนุโลมให้สายได้
    
    attendances = relationship("AttendanceRecord", back_populates="shift")

class AttendanceRecord(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    
    date = Column(Date, nullable=False, index=True)
    
    time_in = Column(Time, nullable=True)
    in_location_lat = Column(Float, nullable=True)
    in_location_lng = Column(Float, nullable=True)
    
    time_out = Column(Time, nullable=True)
    out_location_lat = Column(Float, nullable=True)
    out_location_lng = Column(Float, nullable=True)
    
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.ABSENT)
    
    is_ot_approved = Column(Boolean, default=False)
    total_work_hours = Column(Float, default=0.0)
    ot_hours = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    employee = relationship("Employee", backref="attendances")
    shift = relationship("Shift", back_populates="attendances")
