from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.core.config import templates
from app.core.database import get_db
from app.models.role import RoleTable
from app.services.user_service import UserService
from app.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_class=HTMLResponse)
async def list_users(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login?error=Please Login")
    
    users = UserService.get_all_users(db)
    roles = db.query(RoleTable).all()
    
    return templates.TemplateResponse("users/users.html", {
        "request": request,
        "users": users,
        "user": user,
        "roles": roles
    })

@router.post("/add")
async def add_user(
    username: str = Form(...),
    password: str = Form(...),
    role_id: int = Form(...),         
    db: Session = Depends(get_db)
):
    # สังคายนา: ตัด full_name และ manager_id ออก (ไปอยู่ใน Employee แทน)
    user_data = {
        "username": username,
        "password": password,
        "role_id": role_id,
        "is_active": True
    }
    try:
        UserService.create_user(db, user_data)
        return RedirectResponse(url="/users", status_code=303)
    except Exception as e:
        return {"error": f"Could not create user: {str(e)}"}

@router.post("/update/{user_id}")
async def update_user(
    user_id: int,
    role_id: int = Form(...),
    password: Optional[str] = Form(None), # เพิ่มให้รองรับการเปลี่ยน Password
    db: Session = Depends(get_db)
):
    # สังคายนา: รับแค่ role_id และ password (ถ้ามี)
    update_data = {
        "role_id": role_id
    }
    
    if password and password.strip():
        update_data["password"] = password # UserService ควรมี Logic Hash รหัสตรงนี้

    user = UserService.update_user(db, user_id, update_data)
    if not user:
        return {"error": "User not found"}
    return {"status": "success", "message": "Update successful"}

@router.post("/toggle/{user_id}")
async def toggle_user(user_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user: return {"status": "error"}
    updated_user = UserService.toggle_status(db, user_id)
    return {"status": "success", "new_active_status": updated_user.is_active}

@router.post("/delete/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user: return {"status": "error"}
    UserService.delete_user(db, user_id)
    return {"status": "success"}