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
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.models.user import UserTable
from app.models.role import RoleTable
from app.models.menu import MenuTable

from app.core.config import templates
from app.core.database import engine, Base, get_db
from app.dependencies import get_current_user
from app.services.user_service import UserService
from app.routes import auth, employee, role, menu
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI()

base_path = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(base_path / "static")), name="static")

@app.on_event("startup")
async def startup_event():
    templates.env.globals["get_menus"] = lambda request: getattr(request.state, "menus", [])
    templates.env.globals["get_user"] = lambda request: getattr(request.state, "user", None)
    templates.env.globals["app_config"] = settings

app.include_router(auth.router)
app.include_router(employee.router)
app.include_router(role.router)
app.include_router(menu.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.middleware("http")
async def add_menus_to_state(request: Request, call_next):
    with contextlib.closing(next(get_db())) as db:
        all_menus = db.query(MenuTable).filter(MenuTable.is_active == True).order_by(MenuTable.order).all()
        
        username = request.cookies.get("session_user")
        user = None
        if username:
            user = UserService.get_user_by_username(db, username)
        
        accessible_list = []
        for m in all_menus:
            is_allowed = False
            if not m.required_roles:
                is_allowed = True
            elif user and user.role_data and user.role_data.name in m.required_roles.split(','):
                is_allowed = True
            
            if is_allowed:
                accessible_list.append(m)

        final_tree = []
        for m in accessible_list:
            if m.parent_id is None:
                m.children = [c for c in accessible_list if c.parent_id == m.id]
                final_tree.append(m)
        
        request.state.menus = final_tree
        request.state.user = user 
    
    response = await call_next(request)
    return response

def render(template_name: str, request: Request, context: dict = {}):
    full_context = {"request": request}
    full_context.update(context)
    return templates.TemplateResponse(template_name, full_context)

@app.get("/dashboard")
async def dashboard(request: Request):
    return render("dashboard.html", request, {"total_employees": 10})