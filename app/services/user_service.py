from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import UserTable
from typing import List, Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    def hash_password(password: str):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_user(db: Session, user_data: dict) -> UserTable:
        # 🛠️ สังคายนา: ตัด full_name ออก เพราะ UserTable ตัวใหม่ไม่มีฟิลด์นี้แล้ว
        raw_password = str(user_data.get('password', '1234')) 
        
        # เช็กว่าถ้าเป็น hash มาอยู่แล้วไม่ต้อง hash ซ้ำ
        if not raw_password.startswith('$2b$'):
            password_to_save = UserService.hash_password(raw_password)
        else:
            password_to_save = raw_password

        new_user = UserTable(
            username=user_data.get('username'),
            password=password_to_save,
            role_id=user_data.get('role_id'),
            is_active=user_data.get('is_active', True)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
        
    @staticmethod
    def get_all_users(db: Session) -> List[UserTable]:
        # ใช้ joinedload ได้ถ้าบอสอยากให้ Query ทีเดียวจบ (ลด N+1 Problem)
        return db.query(UserTable).all()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[UserTable]:
        return db.query(UserTable).filter(UserTable.username == username).first()

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: dict):
        user = db.query(UserTable).filter(UserTable.id == user_id).first()
        if user:
            # 1. จัดการเรื่องสิทธิ์ (Role)
            if 'role_id' in user_data:
                user.role_id = user_data.get('role_id')

            # 2. 🛠️ เพิ่มเรื่องเปลี่ยนรหัสผ่าน (จาก Modal ที่เราทำเพิ่ม)
            if 'password' in user_data and user_data['password']:
                raw_pass = user_data['password']
                # ถ้าไม่ได้ส่งมาเป็น Hash อยู่แล้ว ให้ Hash ซะ
                if not raw_pass.startswith('$2b$'):
                    user.password = UserService.hash_password(raw_pass)
                else:
                    user.password = raw_pass

            # 🛠️ สังคายนา: เอา user.full_name และ user.manager_id ออกถาวร
            
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def toggle_status(db: Session, user_id: int):
        user = db.query(UserTable).filter(UserTable.id == user_id).first()
        if user:
            user.is_active = not user.is_active 
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(UserTable).filter(UserTable.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

    @staticmethod
    def get_unlinked_users(db: Session, current_emp_user_id: int = None):
        from app.models.employee import Employee
        
        # หา id ของ User ทั้งหมดที่ถูกผูกกับ Employee ไปแล้ว
        linked_user_ids = db.query(Employee.user_id).filter(Employee.user_id != None)
        
        # ดึง User ที่ไม่อยู่ในกลุ่มที่ผูกแล้ว
        # รวม current_emp_user_id กลับมาเพื่อให้หน้า Edit ของ Employee คนนั้นยังเห็นตัวเองใน List
        if current_emp_user_id:
            return db.query(UserTable).filter(
                (UserTable.id == current_emp_user_id) | (~UserTable.id.in_(linked_user_ids))
            ).all()
            
        return db.query(UserTable).filter(~UserTable.id.in_(linked_user_ids)).all()