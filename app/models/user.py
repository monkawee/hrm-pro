from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)

    # เชื่อมไปที่ RoleTable
    role_id = Column(Integer, ForeignKey("roles.id")) 
    role_data = relationship("app.models.role.RoleTable", back_populates="users")

    # สายงาน (Self-referencing)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager_data = relationship("UserTable", remote_side=[id])

    @property
    def role(self):
        return self.role_data.name if self.role_data else None