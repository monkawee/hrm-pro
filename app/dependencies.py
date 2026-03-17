from fastapi import Request, Depends
from sqlalchemy.orm import Session, joinedload # <--- ต้องมี joinedload
from app.core.database import get_db
from app.models.user import UserTable

def get_current_user(request: Request, db: Session = Depends(get_db)):
    # ดึง ID จาก Session ที่เราเพิ่งแก้ใน auth.py
    user_id = request.session.get("user_id")
    
    if not user_id:
        return None
        
    # 🌟 หัวใจสำคัญคือบรรทัดนี้ครับบอส!
    user = db.query(UserTable)\
             .options(
                 joinedload(UserTable.employee), # ดึงข้อมูล Employee มาเลยไม่ต้องรอ
                 joinedload(UserTable.role)     # ดึงข้อมูล Role มาเลยไม่ต้องรอ
             )\
             .filter(UserTable.id == user_id)\
             .first()
             
    return user

# ฟังก์ชันที่บอสเรียกใน base.html ({% set current_user = get_user(request) %})
# ต้องมั่นใจว่ามันคืนค่า user ที่ผ่าน joinedload มาแล้วนะครับ