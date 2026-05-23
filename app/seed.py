from app.core.database import SessionLocal, engine, Base
from app.services.user_service import UserService

from app.models.user import UserTable
from app.models.role import RoleTable
from app.models.menu import MenuTable
from app.models.employee import Employee, Attachment, AttachmentCategory # เพิ่ม Model ใหม่
from app.models.leave_request import LeaveRequest, LeaveType, LeaveStatus
from app.models.payroll import Payroll, PayrollStatus
from app.models.attendance import AttendanceRecord, Shift, AttendanceStatus
from app.models.performance import PerformanceReview, ReviewStatus
from app.models.training import TrainingCourse, TrainingRecord, TrainingStatus
from app.models.audit import AuditLog
from datetime import date, datetime

def seed_data():
    print("⏳ [1/6] Cleaning old data...")
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # --- 2. Seeding Roles ---
        print("🌱 [2/6] Seeding Roles...")
        roles_data = [
            {"name": "admin", "display_name": "ผู้ดูแลระบบ (Admin)"},
            {"name": "hr", "display_name": "ฝ่ายบุคคล (HR)"},
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
            {"id": 3,"title": "ทะเบียนพนักงาน", "link": "/employees", "icon": "fas fa-address-card", "order": 1, "parent_id": 2, "required_roles": "admin,hr,top_manager"},
            {"id": 4,"title": "ข้อมูลผู้ใช้งานระบบ", "link": "/users", "icon": "fas fa-user-shield", "order": 2, "parent_id": 2, "required_roles": "admin,hr,top_manager"},
            {"id": 5,"title": "กลุ่มผู้ใช้งานระบบ", "link": "/roles", "icon": "fas fa-users-cog", "order": 3, "parent_id": 2, "required_roles": "admin,hr,top_manager"},
            {"id": 6, "title": "ระบบการลา", "link": "#", "icon": "fas fa-calendar-check", "order": 3, "parent_id": None},
            {"id": 7,"title": "ประวัติการลา/อนุมัติ", "link": "/leaves", "icon": "fas fa-history", "order": 1, "parent_id": 6},
            {"id": 8,"title": "ยื่นใบลา", "link": "/leaves/request", "icon": "fas fa-file-signature", "order": 2, "parent_id": 6},
            {"id": 9,"title": "ระบบเงินเดือน", "link": "#", "icon": "fas fa-money-check-dollar", "order": 5, "parent_id": None},
            {"id": 10,"title": "ประวัติเงินเดือน", "link": "/payroll", "icon": "fas fa-file-invoice-dollar", "order": 1, "parent_id": 9},
            {"id": 11,"title": "ระบบเวลาเข้างาน", "link": "#", "icon": "fas fa-clock", "order": 4, "parent_id": None},
            {"id": 12,"title": "ลงเวลาทำงาน", "link": "/attendance/check", "icon": "fas fa-fingerprint", "order": 1, "parent_id": 11},
            {"id": 13,"title": "ประวัติลงเวลา", "link": "/attendance/history", "icon": "fas fa-history", "order": 2, "parent_id": 11},
            {"id": 14,"title": "รายงานเวลาทำงาน", "link": "/attendance/report", "icon": "fas fa-file-export", "order": 3, "parent_id": 11, "required_roles": "admin,hr,top_manager"},
            {"id": 15,"title": "การประเมินผล", "link": "#", "icon": "fas fa-star", "order": 6, "parent_id": None},
            {"id": 16,"title": "ประเมินพนักงาน", "link": "/performance/evaluate", "icon": "fas fa-user-check", "order": 1, "parent_id": 15, "required_roles": "admin,hr,top_manager,manager"},
            {"id": 17,"title": "ดูผลประเมิน", "link": "/performance", "icon": "fas fa-chart-bar", "order": 2, "parent_id": 15},
            {"id": 18,"title": "การฝึกอบรม", "link": "/training", "icon": "fas fa-graduation-cap", "order": 7, "parent_id": None},
            {"id": 19,"title": "ระบบความปลอดภัย", "link": "#", "icon": "fas fa-shield-alt", "order": 8, "parent_id": None, "required_roles": "admin,hr,top_manager"},
            {"id": 20,"title": "Audit Logs", "link": "/security/audit", "icon": "fas fa-history", "order": 1, "parent_id": 19, "required_roles": "admin,hr,top_manager"},
            {"id": 21,"title": "ตั้งค่าเมนู", "link": "/menus", "icon": "fas fa-list-check", "order": 9, "parent_id": None, "required_roles": "admin,hr,top_manager"}
        ]
        for m in menus_data:
            db.add(MenuTable(**m))
        db.commit()

        # --- 4. Seeding Users (สร้าง User รอไว้ก่อน) ---
        print("🌱 [4/6] Seeding Users...")
        users_data = [
            {"full_name": "Administrator", "username": "admin", "password": "123", "role_id": role_map["admin"]},
            {"full_name": "HR Master", "username": "hr", "password": "123", "role_id": role_map["hr"]},
            {"full_name": "Top Manager Boss", "username": "topmanager", "password": "123", "role_id": role_map["top_manager"]},
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
            {"code": "EMP001", "fname": "Super", "lname": "Administrator", "user_key": "admin", "salary": 60000, "manager_code": None},
            {"code": "EMP005", "fname": "C Level", "lname": "Boss", "user_key": "topmanager", "salary": 150000, "manager_code": None},
            {"code": "EMP002", "fname": "HR", "lname": "Master", "user_key": "hr", "salary": 50000, "manager_code": "EMP005"},
            {"code": "EMP003", "fname": "John", "lname": "Manager", "user_key": "manager1", "salary": 45000, "manager_code": "EMP005"},
            {"code": "EMP004", "fname": "Somchai", "lname": "Staff", "user_key": "staff1", "salary": 20000, "manager_code": "EMP003"}
        ]
        
        emp_obj_map = {}
        for e in emp_payload:
            manager_id = emp_obj_map[e["manager_code"]] if e["manager_code"] else None
            new_emp = Employee(
                employee_code=e["code"],
                first_name=e["fname"],
                last_name=e["lname"],
                user_id=user_map[e["user_key"]], 
                manager_id=manager_id,
                join_date=date(2024, 1, 1),
                base_salary=e["salary"]
            )
            db.add(new_emp)
            db.flush()
            emp_obj_map[e["code"]] = new_emp.id
            # ... (เพิ่ม Attachment ตามเดิม) ...

        db.commit()

        # --- 6. Seeding Shifts ---
        print("🌱 [6/6] Seeding Shifts...")
        default_shift = Shift(
            name="กะปกติ (09:00 - 18:00)",
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("18:00", "%H:%M").time(),
            late_grace_period=15
        )
        db.add(default_shift)
        db.commit()

        # --- 7. Seeding Training Courses ---
        print("🌱 [7/7] Seeding Training Courses...")
        courses_data = [
            {"name": "ปฐมนิเทศพนักงานใหม่ (Orientation)", "description": "การปรับตัวและเรียนรู้วัฒนธรรมองค์กร", "iso_code": "HR-01", "trainer": "HR Team"},
            {"name": "ความปลอดภัยในการทำงาน (Safety First)", "description": "หลักสูตรความปลอดภัยตามมาตรฐานสากล", "iso_code": "ISO45001", "trainer": "Safety Officer"},
            {"name": "PDPA Awareness", "description": "ความรู้เรื่องกฎหมายคุ้มครองข้อมูลส่วนบุคคล", "iso_code": "PDPA-01", "trainer": "Legal Team"}
        ]
        for c in courses_data:
            db.add(TrainingCourse(**c))
        db.commit()

        print("✨ Seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()