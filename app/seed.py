# ==========================================================
# COMMAND TO RUN (Copy & Paste in Terminal):
# python -m app.seed
# ==========================================================

from app.core.database import SessionLocal, engine, Base
from app.services.user_service import UserService
from app.models.user import UserTable, RoleTable  # Import Table มาใช้งานตรงๆ

def seed_data():
    print("⏳ [1/4] Cleaning old data...")
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. สร้าง Roles ก่อน (หัวใจสำคัญของระบบใหม่)
        print("🌱 [2/4] Seeding Roles...")
        roles_data = [
            {"name": "top_manager", "display_name": "Admin"},
            {"name": "manager", "display_name": "Manager"},
            {"name": "employee", "display_name": "Staff"}
        ]
        
        for r in roles_data:
            role = RoleTable(name=r["name"], display_name=r["display_name"])
            db.add(role)
        db.commit()
        print("✅ Roles created: Admin, Manager, Staff")

        # 2. เตรียมข้อมูล User
        # หมายเหตุ: เราส่ง 'role_name' ไปให้ Service เดี๋ยวให้ Service ไปหา id เอาเอง
        print("🌱 [3/4] Seeding Users...")
        users_to_create = [
            {"full_name": "Senior Boss", "username": "admin", "password": "1234", "role_name": "top_manager", "manager_id": None},
            {"full_name": "John Manager", "username": "manager1", "password": "1234", "role_name": "manager", "manager_id": None},
            {"full_name": "Somchai Staff", "username": "staff1", "password": "1234", "role_name": "employee", "manager_id": 2}
        ]

        for u_data in users_to_create:
            # 1. หา Role ID จากชื่อก่อนส่ง
            role_obj = db.query(RoleTable).filter(RoleTable.name == u_data["role_name"]).first()
            
            # 2. ปรับข้อมูลให้พร้อม (ส่งแค่ role_id ที่เป็นเลข)
            u_data["role_id"] = role_obj.id if role_obj else None
            
            # 3. เช็คและสร้าง
            existing_user = UserService.get_user_by_username(db, u_data["username"])
            if not existing_user:
                UserService.create_user(db, u_data)
                print(f"✅ Created User: {u_data['username']}")
            else:
                print(f"⚠️ Skipped: {u_data['username']} (Already exists)")

        print("✨ [4/4] Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()