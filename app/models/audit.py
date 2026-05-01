from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Can be null if failed login
    
    action = Column(String(100), nullable=False) # e.g., "LOGIN", "EXPORT_PAYROLL", "CREATE_USER"
    ip_address = Column(String(50), nullable=True)
    details = Column(String(255), nullable=True)
    
    timestamp = Column(DateTime, default=datetime.now)
    
    user = relationship("UserTable", backref="audit_logs")
