# app/routes/employee.py
from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.templating import Jinja2Templates

from app.core.config import templates
from app.core.database import get_db
from app.models.role import RoleTable
from app.services.user_service import UserService
from app.dependencies import get_current_user

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_class=HTMLResponse)
async def list_employees(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login?error=Please Login")
    
    employees = UserService.get_all_users(db)
    roles = db.query(RoleTable).all()
    managers = [u for u in employees if u.role in ["manager", "top_manager"]]
    
    return templates.TemplateResponse("employees/employees.html", {
        "request": request,
        "employees": employees,
        "managers": managers,
        "user": user,
        "roles": roles
    })

@router.post("/add")
async def add_employee(
    full_name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    role_id: int = Form(...),         
    manager_id: Optional[int] = Form(None), 
    db: Session = Depends(get_db)
):
    user_data = {
        "full_name": full_name,
        "username": username,
        "password": password,
        "role_id": role_id,
        "manager_id": manager_id if manager_id != 0 else None 
    }
    try:
        UserService.create_user(db, user_data)
        return RedirectResponse(url="/employees", status_code=303)
    except Exception as e:
        return {"error": f"Could not create user: {str(e)}"}

@router.post("/toggle/{user_id}")
async def toggle_employee(user_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user: return {"status": "error"}
    updated_user = UserService.toggle_status(db, user_id)
    return {"status": "success", "new_active_status": updated_user.is_active}

@router.post("/delete/{user_id}")
async def delete_employee(user_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user: return {"status": "error"}
    UserService.delete_user(db, user_id)
    return {"status": "success"}

@router.post("/update/{user_id}")
async def update_employee(
    user_id: int,
    full_name: str = Form(...),
    role_id: int = Form(...),
    manager_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
):
    update_data = {
        "full_name": full_name,
        "role_id": role_id,              
        "manager_id": manager_id if manager_id != 0 else None
    }
    user = UserService.update_user(db, user_id, update_data)
    if not user:
        return {"error": "User not found"}
    return {"message": "Update successful"}