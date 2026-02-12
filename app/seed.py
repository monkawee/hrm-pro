from app.core.database import SessionLocal, engine, Base
from app.models.user import UserTable, UserRole

def seed_data():
    # 1. สร้าง Table ถ้ายังไม่มี (และล้างข้อมูลเก่าเพื่อความสะอาดของ Demo)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 2. เตรียมข้อมูล Mockup สำหรับ Roles ต่างๆ
        users = [
            UserTable(
                username="admin",
                password="1234", # ในระบบจริงต้อง Hash
                full_name="บอส ใหญ่สุด (CEO)",
                role=UserRole.TOP_MANAGER,
                is_active=True
            ),
            UserTable(
                username="hr01",
                password="1234",
                full_name="สมหญิง งานไว (HR)",
                role=UserRole.HR,
                is_active=True
            ),
            UserTable(
                username="manager01",
                password="1234",
                full_name="หัวหน้า สมศักดิ์",
                role=UserRole.MANAGER,
                is_active=True
            ),
            UserTable(
                username="staff01",
                password="1234",
                full_name="พนักงาน ทดลองงาน",
                role=UserRole.EMPLOYEE,
                is_active=False # ลองให้คนนี้โดนปิดกั้นไว้
            ),
        ]

        # 3. บันทึกลง Database
        db.add_all(users)
        db.commit()
        print("✅ Seed data completed successfully!")
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()