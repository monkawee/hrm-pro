from app.core.database import SessionLocal, engine, Base
from app.services.user_service import UserService

from app.models.user import UserTable
from app.models.role import RoleTable
from app.models.menu import MenuTable
from app.models.employee import Employee, Attachment, AttachmentCategory # เพิ่ม Model ใหม่
from app.models.leave_request import LeaveRequest, LeaveType, LeaveStatus
from datetime import date

def seed_data():
    print("⏳ [1/6] Cleaning old data...")
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # --- 2. Seeding Roles ---
        print("🌱 [2/6] Seeding Roles...")
        roles_data = [
            {"name": "hr", "display_name": "ฝ่ายบุคคล (Admin)"},
            {"name": "top_manager", "display_name": "ผู้บริหาร (Top Manager)"},
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

        # --- 3. Seeding Menus ---
        print("🌱 [3/6] Seeding Menus...")
        menus_data = [
            {"id": 1,"title": "Dashboard", "link": "/dashboard", "icon": "fas fa-chart-line", "order": 1, "parent_id": None},
            {"id": 2, "title": "จัดการบุคลากร", "link": "#", "icon": "fas fa-users-gear", "order": 2, "parent_id": None},
            # ปรับเมนูลูกให้สอดคล้องกับ Module 6
            {"id": 3,"title": "ทะเบียนพนักงาน", "link": "/employees", "icon": "fas fa-address-card", "order": 1, "parent_id": 2, "required_roles": "top_manager,manager"},
            {"id": 4,"title": "ข้อมูลผู้ใช้งานระบบ", "link": "/users", "icon": "fas fa-user-shield", "order": 2, "parent_id": 2, "required_roles": "top_manager"},
            {"id": 5,"title": "กลุ่มผู้ใช้งานระบบ", "link": "/roles", "icon": "fas fa-users-cog", "order": 3, "parent_id": 2, "required_roles": "top_manager"},
            {"id": 6, "title": "ระบบการลา", "link": "#", "icon": "fas fa-calendar-check", "order": 3, "parent_id": None},
            {"id": 7,"title": "ประวัติการลา/อนุมัติ", "link": "/leaves", "icon": "fas fa-history", "order": 1, "parent_id": 6},
            {"id": 8,"title": "ยื่นใบลา", "link": "/leaves/request", "icon": "fas fa-file-signature", "order": 2, "parent_id": 6},
            {"id": 9,"title": "ตั้งค่าเมนู", "link": "/menus", "icon": "fas fa-list-check", "order": 4, "parent_id": None, "required_roles": "top_manager"}
        ]
        for m in menus_data:
            db.add(MenuTable(**m))
        db.commit()

        # --- 4. Seeding Users (สร้าง User รอไว้ก่อน) ---
        print("🌱 [4/6] Seeding Users...")
        users_data = [
            {"full_name": "Admin Boss", "username": "admin", "password": "123", "role_id": role_map["top_manager"]},
            {"full_name": "Manager John", "username": "manager1", "password": "123", "role_id": role_map["manager"]},
            {"full_name": "Staff Somchai", "username": "staff1", "password": "123", "role_id": role_map["employee"]}
        ]
        user_map = {}
        for u in users_data:
            new_user = UserService.create_user(db, u) # สมมติว่าคืนค่า user object กลับมา
            user_map[u["username"]] = new_user.id

        # --- 5. Seeding Employees (สร้างพนักงานมาผูกกับ User ID) ---
        print("🌱 [5/6] Seeding Employees & Documents...")
        emp_payload = [
            {"code": "EMP001", "fname": "Senior", "lname": "Boss", "user_key": "admin"},
            {"code": "EMP002", "fname": "John", "lname": "Manager", "user_key": "manager1"},
            {"code": "EMP003", "fname": "Somchai", "lname": "Staff", "user_key": "staff1"}
        ]
        
        for e in emp_payload:
            new_emp = Employee(
                employee_code=e["code"],
                first_name=e["fname"],
                last_name=e["lname"],
                user_id=user_map[e["user_key"]], # ผูกตรงนี้!
                join_date=date(2024, 1, 1)
            )
            db.add(new_emp)
            # ... (เพิ่ม Attachment ตามเดิม) ...

        db.commit()
        print("✨ [6/6] Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()