from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class MenuTable(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    link = Column(String)
    icon = Column(String)
    order = Column(Integer)
    is_active = Column(Boolean, default=True)
    required_roles = Column(String, nullable=True) # เก็บเป็น "admin,manager"