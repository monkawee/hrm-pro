from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base

class RoleTable(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # เช่น 'admin', 'manager'
    display_name = Column(String, nullable=False)                 # เช่น 'ผู้ดูแลระบบ', 'ผู้จัดการ'
    users = relationship("UserTable", back_populates="role")
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Role name={self.name} display_name={self.display_name}>"