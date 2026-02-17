from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class MenuTable(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    link = Column(String)
    icon = Column(String)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    required_roles = Column(String, nullable=True)
    
    parent_id = Column(Integer, ForeignKey("menus.id"), nullable=True)
    
    sub_menus = relationship("MenuTable", 
                             backref="parent", 
                             remote_side=[id], 
                             order_by="MenuTable.order")