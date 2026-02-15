from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.role import RoleTable
from fastapi import HTTPException, status

class RoleService:
    @staticmethod
    def get_all_roles(db: Session, only_active: bool = False):
        query = db.query(RoleTable)
        if only_active:
            query = query.filter(RoleTable.is_active == True)
        return query.order_by(RoleTable.id.asc()).all()

    @staticmethod
    def create_role(db: Session, name: str, display_name: str):
        # 1. เช็คก่อนว่า System Name นี้มีหรือยัง (ป้องกัน Unique Constraint Error)
        existing = db.query(RoleTable).filter(RoleTable.name == name).first()
        if existing:
            raise HTTPException(status_code=400, detail="System Name นี้มีอยู่ในระบบแล้ว")
        
        try:
            new_role = RoleTable(name=name, display_name=display_name)
            db.add(new_role)
            db.commit()
            db.refresh(new_role)
            return new_role
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def update_role(db: Session, role_id: int, display_name: str, is_active: bool):
        role = db.query(RoleTable).filter(RoleTable.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="ไม่พบตำแหน่งที่ต้องการแก้ไข")
        
        role.display_name = display_name
        role.is_active = is_active
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def delete_role(db: Session, role_id: int):
        role = db.query(RoleTable).filter(RoleTable.id == role_id).first()
        if not role:
            return False

        try:
            db.delete(role)
            db.commit()
            return True
        except IntegrityError:
            # 2. ดักเคสที่มี Foreign Key ผูกอยู่ (พนักงานยังใช้ Role นี้)
            db.rollback()
            raise HTTPException(
                status_code=400, 
                detail="ไม่สามารถลบได้ เนื่องจากยังมีพนักงานที่ใช้ตำแหน่งนี้อยู่ในระบบ"
            )
        except Exception as e:
            db.rollback()
            raise e