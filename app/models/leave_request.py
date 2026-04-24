from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import Base

class LeaveType(enum.Enum):
    SICK = "sick"
    VACATION = "vacation"
    PERSONAL = "personal"
    OTHERS = "others"

class LeaveStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    
    leave_type = Column(Enum(LeaveType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    reason = Column(Text, nullable=False)
    
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False)
    manager_comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    employee = relationship("Employee", backref="leave_requests")
