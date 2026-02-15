from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class RoleTable(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) 
    display_name = Column(String) 
    is_active = Column(Boolean, default=True)
    users = relationship("UserTable", back_populates="role_data")