from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import Base

class ReviewStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"

class PerformanceReview(Base):
    __tablename__ = "performance_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Evaluated by manager
    
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    
    kpi_score = Column(Float, default=0.0)
    feedback = Column(Text, nullable=True)
    
    status = Column(Enum(ReviewStatus), default=ReviewStatus.DRAFT)
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    employee = relationship("Employee", backref="performance_reviews")
    reviewer = relationship("UserTable", foreign_keys=[reviewer_id])
