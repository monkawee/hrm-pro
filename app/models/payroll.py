from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import Base

class PayrollStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"

class Payroll(Base):
    __tablename__ = "payrolls"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    
    basic_salary = Column(Integer, default=0)
    deductions = Column(Integer, default=0)
    net_salary = Column(Integer, default=0)
    
    status = Column(Enum(PayrollStatus), default=PayrollStatus.PENDING)
    payment_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    
    employee = relationship("Employee", backref="payrolls")
