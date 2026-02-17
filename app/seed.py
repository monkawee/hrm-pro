# ==========================================================
# COMMAND TO RUN (Copy & Paste in Terminal):
# python -m app.seed
# ==========================================================
# ==========================================================
# COMMAND TO RUN (Copy & Paste in Terminal):
# python -m app.seed
# ==========================================================

from app.core.database import SessionLocal, engine, Base
from app.services.user_service import UserService

from app.models.user import UserTable
from app.models.role import RoleTable
from app.models.menu import MenuTable

def seed_data():
    print("⏳ [1/5] Cleaning old data...")
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("🌱 [2/5] Seeding Roles...")
        roles_data = [
            {"name": "top_manager", "display_name": "ผู้บริหาร (Admin)"},
            {"name": "manager", "display_name": "หัวหน้างาน (Manager)"},
            {"name": "employee", "display_name": "พนักงานทั่วไป (Staff)"}
        ]
        
        role_map = {}
        for r in roles_data:
            role_obj = RoleTable(name=r["name"], display_name=r["display_name"])
            db.add(role_obj)
            db.flush() 
            role_map[r["name"]] = role_obj.id
        
        db.commit()
        print(f"✅ Created {len(roles_data)} roles.")

        print("🌱 [3/5] Seeding Menus...")
        menus_data = [
            # เมนูหลักเดี่ยวๆ
            {"title": "Dashboard", "link": "/dashboard", "icon": "fas fa-chart-line", "order": 1, "parent_id": None},
            
            # เมนูหลักที่มีลูก (ตั้ง link เป็น # หรือ path กลาง)
            {"id": 2, "title": "จัดการบุคลากร", "link": "#", "icon": "fas fa-users-gear", "order": 2, "parent_id": None},
            
            # เมนูลูก (parent_id = 2)
            {"title": "รายชื่อพนักงาน", "link": "/employees", "icon": "fas fa-user-group", "order": 1, "parent_id": 2, "required_roles": "top_manager,manager"},
            {"title": "จัดการตำแหน่ง", "link": "/roles", "icon": "fas fa-briefcase", "order": 2, "parent_id": 2, "required_roles": "top_manager"},
            
            # เมนูตั้งค่า
            {"title": "ตั้งค่าเมนู", "link": "/menus", "icon": "fas fa-list-check", "order": 3, "parent_id": None, "required_roles": "top_manager"}
        ]
        
        for m in menus_data:
            db.add(MenuTable(**m))
        db.commit()
        print(f"✅ Created {len(menus_data)} dynamic menus.")

        print("🌱 [4/5] Seeding Users...")
        users_to_create = [
            {
                "full_name": "Senior Boss", 
                "username": "admin", 
                "password": "123", 
                "role_id": role_map["top_manager"], 
                "manager_id": None
            },
            {
                "full_name": "John Manager", 
                "username": "manager1", 
                "password": "123", 
                "role_id": role_map["manager"], 
                "manager_id": None
            },
            {
                "full_name": "Somchai Staff", 
                "username": "staff1", 
                "password": "123", 
                "role_id": role_map["employee"], 
                "manager_id": 2 
            }
        ]

        for u_data in users_to_create:
            UserService.create_user(db, u_data)
            print(f"✅ Created User: {u_data['username']}")

        print("✨ [5/5] Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()