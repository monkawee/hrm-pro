from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    
    # --- Relationships ---
    role = relationship("RoleTable", back_populates="users")
    employee = relationship("Employee", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User username={self.username} role_id={self.role_id}>"