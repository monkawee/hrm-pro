from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import UserTable, RoleTable
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
        actual_role_id = user_data.get('role_id')

        raw_password = str(user_data.get('password', '1234')) 
        
        print(f"DEBUG: Processing password for {user_data.get('username')} (Length: {len(raw_password)})")

        if raw_password.startswith('$2b$'):
            password_to_save = raw_password
        else:
            safe_password = raw_password[:71] 
            password_to_save = UserService.hash_password(safe_password)

        new_user = UserTable(
            full_name=user_data.get('full_name'),
            username=user_data.get('username'),
            password=password_to_save,
            role_id=actual_role_id,
            manager_id=user_data.get('manager_id'),
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
        
    @staticmethod
    def get_all_users(db: Session) -> List[UserTable]:
        return db.query(UserTable).all()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[UserTable]:
        return db.query(UserTable).filter(UserTable.username == username).first()

    @staticmethod
    def toggle_status(db: Session, user_id: int):
        user = db.query(UserTable).filter(UserTable.id == user_id).first()
        if user:
            user.is_active = not user.is_active 
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: dict):
        user = db.query(UserTable).filter(UserTable.id == user_id).first()
        if user:
            user.full_name = user_data.get('full_name', user.full_name)
            
            if 'role_id' in user_data:
                user.role_id = user_data.get('role_id')
            elif 'role' in user_data:
                user.role_id = user_data.get('role')

            user.manager_id = user_data.get('manager_id') if user_data.get('manager_id') != 0 else None
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