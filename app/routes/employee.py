from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.employee_service import EmployeeService
from app.services.user_service import UserService
from app.dependencies import get_current_user
from app.core.config import templates
from datetime import datetime

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_class=HTMLResponse)
async def list_employees(
    request: Request, 
    db: Session = Depends(get_db), 
    user = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
    
    employees = EmployeeService.get_all(db)
    # ดึง User ทั้งหมดที่ยังไม่ได้ผูกกับใคร (สำหรับหน้า Add/Edit)
    unlinked_users = UserService.get_unlinked_users(db)
    
    # return templates.TemplateResponse("employees/employees.html", {
    #     "request": request,
    #     "employees": employees,
    #     "unlinked_users": unlinked_users,
    #     "user": user,
    #     "today": datetime.now().strftime("%Y-%m-%d")
    # })
    return templates.TemplateResponse(
        request=request, 
        name="employees/employees.html", 
        context={
            "user": user,
            "employees": employees,
            "unlinked_users": unlinked_users,
            "today": datetime.now().strftime("%Y-%m-%d")
        }
    )

@router.post("/add")
async def add_employee(
    employee_code: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(None),
    join_date: str = Form(...),
    manager_id: str = Form(None),
    user_id: str = Form(None),
    db: Session = Depends(get_db)
):
    emp_payload = {
        "employee_code": employee_code,
        "first_name": first_name,
        "last_name": last_name,
        "email": email if email else None,
        "join_date": datetime.strptime(join_date, "%Y-%m-%d").date(),
        "manager_id": int(manager_id) if manager_id and manager_id != '0' else None,
        "user_id": int(user_id) if user_id and user_id != '0' else None
    }
    EmployeeService.create_employee(db, emp_payload)
    return RedirectResponse(url="/employees", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/update/{emp_id}")
async def update_employee(
    emp_id: int,
    first_name: str = Form(None),
    last_name: str = Form(None),
    email: str = Form(None),
    join_date: str = Form(None),
    manager_id: str = Form(None),
    user_id: str = Form(None),
    db: Session = Depends(get_db)  # <--- เช็กว่ามีอันนี้
):
    update_data = {}
    if first_name: update_data["first_name"] = first_name
    if last_name: update_data["last_name"] = last_name
    if email: update_data["email"] = email
    if join_date: 
        update_data["join_date"] = datetime.strptime(join_date, "%Y-%m-%d").date()
    
    # จัดการเรื่องค่าว่างให้เป็น None เพื่อบันทึกลง DB เป็น NULL
    update_data["manager_id"] = int(manager_id) if manager_id and manager_id != '0' else None
    update_data["user_id"] = int(user_id) if user_id and user_id != '0' else None

    # ส่ง db เข้าไปด้วย!
    EmployeeService.update_employee(db, emp_id, update_data) 
    return {"status": "success"}

@router.post("/delete/{emp_id}")
async def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    success = EmployeeService.delete_employee(db, emp_id)
    if success:
        return {"message": "Deleted"}
    return {"message": "Employee not found"}, 404