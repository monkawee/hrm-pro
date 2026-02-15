# app/routes/role.py
from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.role_service import RoleService
from app.dependencies import get_current_user
from app.core.config import templates # ใช้ของกลางที่เราเพิ่งสร้าง

router = APIRouter(prefix="/roles", tags=["Roles"])

# --- 1. หน้าแสดงรายชื่อ Roles ---
@router.get("/", response_class=HTMLResponse)
async def list_roles(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login")
    
    # ดึงข้อมูลผ่าน Service
    roles = RoleService.get_all_roles(db)
    
    return templates.TemplateResponse("roles/roles.html", {
        "request": request, 
        "roles": roles, 
        "user": user
    })

# --- 2. API เพิ่ม Role ใหม่ ---
@router.post("/add")
async def add_role(
    name: str = Form(...), 
    display_name: str = Form(...), 
    db: Session = Depends(get_db)
):
    # ส่งงานต่อให้ Service เป็นคนจัดการ
    RoleService.create_role(db, name=name, display_name=display_name)
    return RedirectResponse(url="/roles", status_code=status.HTTP_303_SEE_OTHER)

# --- 3. API อัปเดต Role ---
@router.post("/update/{role_id}")
async def update_role(
    role_id: int,
    display_name: str = Form(...),
    is_active: str = Form("false"),
    db: Session = Depends(get_db)
):
    active_bool = True if is_active.lower() == "true" else False
    RoleService.update_role(db, role_id, display_name, active_bool)
    return {"message": "Updated success"}

# --- 4. API ลบ Role ---
@router.post("/delete/{role_id}")
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    success = RoleService.delete_role(db, role_id)
    if success:
        return {"message": "Deleted"}
    return {"message": "Role not found"}, 404