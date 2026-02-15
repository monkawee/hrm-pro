from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class RoleTable(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) 
    display_name = Column(String) 
    
    users = relationship("UserTable", back_populates="role_data")

class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)

    role_id = Column(Integer, ForeignKey("roles.id")) 
    role_data = relationship("RoleTable", back_populates="users")

    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager_data = relationship("UserTable", remote_side=[id])

    @property
    def role(self):
        return self.role_data.name if self.role_data else None