# ==========================================================
# COMMAND TO START APP (Run from Project Root):
#
# 1. แบบปกติ (เห็น Error แบบ Real-time):
# uvicorn app.main:app --reload
#
# 2. แบบกำหนด Port เอง (เผื่อ 8000 โดนแย่ง):
# uvicorn app.main:app --reload --port 8080
#
# 3. แบบให้เครื่องอื่นในวง LAN เข้ามาดู Demo ได้:
# uvicorn app.main:app --reload --host 0.0.0.0
# ==========================================================
import os
import contextlib
from pathlib import Path
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, joinedload # ✅ เพิ่ม joinedload

from app.models.user import UserTable
from app.models.role import RoleTable
from app.models.menu import MenuTable

from app.core.config import templates
from app.core.database import engine, Base, get_db
from app.dependencies import get_current_user
from app.services.user_service import UserService
from app.routes import auth, user, role, menu, employee, dashboard, leave, payroll
from app.api import mobile_api
from app.core.config import settings

# สร้างตารางถ้ายังไม่มี
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 1. เขียนฟังก์ชัน Middleware ก่อน
@app.middleware("http")
async def add_data_to_state(request: Request, call_next):
    # ป้องกัน Error กรณี Middleware ทำงานผิดลำดับ
    user_id = None
    if "session" in request.scope:
        user_id = request.session.get("user_id")
    # ตรงนี้ request.session จะยังไม่มีถ้าเราแอด SessionMiddleware ไว้ข้างบนฟังก์ชันนี้
    with contextlib.closing(next(get_db())) as db:
        # ... โค้ดดึงข้อมูลเมนู/User ...
        user_id = request.session.get("user_id") if "session" in request.scope else None
        # ...
    
    response = await call_next(request)
    return response



base_path = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(base_path / "static")), name="static")

@app.on_event("startup")
async def startup_event():
    templates.env.globals["get_menus"] = lambda request: getattr(request.state, "menus", [])
    templates.env.globals["get_user"] = lambda request: getattr(request.state, "user", None)
    templates.env.globals["app_config"] = settings

# Register Routes
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(role.router)
app.include_router(menu.router)
app.include_router(employee.router)
app.include_router(leave.router)
app.include_router(payroll.router)
app.include_router(mobile_api.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

# 🌟 Middleware มหาอุด (แก้ปัญหา Session หลุดและจัดการเมนู)
@app.middleware("http")
async def add_data_to_state(request: Request, call_next):
    with contextlib.closing(next(get_db())) as db:
        # 1. ดึง User จาก Session (ใช้ user_id ตาม auth.py)
        user_id = request.session.get("user_id")
        user = None
        
        if user_id:
            # ✅ ใช้ joinedload เพื่อสอย Employee และ Role มาเก็บไว้ใน state เลย
            user = db.query(UserTable)\
                     .options(joinedload(UserTable.employee), joinedload(UserTable.role))\
                     .filter(UserTable.id == user_id)\
                     .first()
        
        request.state.user = user

        # 2. จัดการเมนูตามสิทธิ์ (RBAC)
        all_menus = db.query(MenuTable).filter(MenuTable.is_active == True).order_by(MenuTable.order).all()
        
        accessible_list = []
        for m in all_menus:
            is_allowed = False
            # ถ้าไม่ระบุ Role ให้เข้าได้ทุกคน หรือ เช็กว่า Role ของ User ตรงกับที่เมนูต้องการไหม
            if not m.required_roles:
                is_allowed = True
            elif user and user.role and user.role.name in m.required_roles.split(','):
                is_allowed = True
            
            if is_allowed:
                accessible_list.append(m)

        # สร้าง Menu Tree สำหรับ Sidebar
        final_tree = []
        for m in accessible_list:
            if m.parent_id is None:
                # ผูกลูกๆ เข้ากับเมนูแม่
                m.children = [c for c in accessible_list if c.parent_id == m.id]
                final_tree.append(m)
        
        request.state.menus = final_tree
    
    response = await call_next(request)
    return response

# ✅ ต้องวาง SessionMiddleware ไว้ก่อน Router
app.add_middleware(
    SessionMiddleware, 
    secret_key="HRM_PRO_SECRET_KEY_9528", 
    session_cookie="hrm_session"
)

# Helper สำหรับการ Render Template
def render(template_name: str, request: Request, context: dict = {}):
    full_context = {"request": request}
    full_context.update(context)
    return templates.TemplateResponse(template_name, full_context)