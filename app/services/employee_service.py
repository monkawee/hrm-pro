from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from app.models.employee import Employee, Attachment, AttachmentCategory
from sqlalchemy import delete
from datetime import date

class EmployeeService:
    # --- 1. ส่วนจัดการพนักงาน (CRUD) ---

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Employee).offset(skip).limit(limit).all()

    @staticmethod
    def get_employee(db: Session, employee_id: int):
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def create_employee(db: Session, emp_data: dict):
        """
        รับ dict ที่มีฟิลด์: employee_code, first_name, last_name, email, join_date, 
        user_id (optional), manager_id (optional)
        """
        # เช็คว่ารหัสพนักงานซ้ำไหม
        existing = db.query(Employee).filter(Employee.employee_code == emp_data.get("employee_code")).first()
        if existing:
            raise HTTPException(status_code=400, detail="รหัสพนักงานนี้มีในระบบแล้ว")

        new_emp = Employee(**emp_data)
        db.add(new_emp)
        try:
            db.commit()
            db.refresh(new_emp)
            return new_emp
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"สร้างพนักงานไม่สำเร็จ: {str(e)}")

    @staticmethod
    def update_employee(db: Session, employee_id: int, update_data: dict):
        """
        อัปเดตข้อมูลพนักงานแบบ Partial (ส่งมาเฉพาะฟิลด์ที่จะแก้)
        """
        db_obj = db.query(Employee).filter(Employee.id == employee_id).first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="ไม่พบพนักงาน")

        for key, value in update_data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"อัปเดตข้อมูลไม่สำเร็จ: {str(e)}")

    @staticmethod
    def delete_employee(db: Session, employee_id: int):
        db_obj = db.query(Employee).filter(Employee.id == employee_id).first()
        if db_obj:
            db.delete(db_obj)
            db.commit()
            return True
        return False

    # --- 2. ส่วนจัดการไฟล์ (Binary VARBINARY) ---

    @staticmethod
    async def process_attachment_upload(db: Session, employee_id: int, category: AttachmentCategory, file: UploadFile):
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลพนักงาน")

        file_content = await file.read()

        # Overwrite Logic: ถ้าเป็นโปรไฟล์หรือบัตรประชาชน ให้ลบใบเดิมก่อน
        if category in [AttachmentCategory.PROFILE, AttachmentCategory.IDENTIFICATION]:
            db.execute(
                delete(Attachment).where(
                    Attachment.employee_id == employee_id,
                    Attachment.category == category
                )
            )

        new_file = Attachment(
            employee_id=employee_id,
            category=category,
            file_name=file.filename,
            file_type=file.content_type,
            file_data=file_content
        )
        
        db.add(new_file)
        try:
            db.commit()
            db.refresh(new_file)
            return {"status": "success", "id": new_file.id, "filename": file.filename}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"บันทึกไฟล์ไม่สำเร็จ: {str(e)}")

    @staticmethod
    def get_attachment_data(db: Session, attachment_id: int):
        return db.query(Attachment).filter(Attachment.id == attachment_id).first()