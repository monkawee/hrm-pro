import os
import contextlib
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import joinedload

from app.models.user import UserTable
from app.models.menu import MenuTable
from app.core.config import templates, settings
from app.core.database import engine, Base, get_db
from app.seed import seed_data  # ✅ ดึงฟังก์ชันมาจาก seed.py ของพี่ไม้
from app.routes import auth, user, role, menu, employee, dashboard, leave, payroll, attendance, performance, training, security
from app.services.audit_service import AuditService
from app.api import mobile_api
from app.core.i18n import get_translator

app = FastAPI(title="HRM PRO - Enterprise Demo")

# --- 1. Startup Event ---
@app.on_event("startup")
async def startup_event():
    # ตั้งค่า Global สำหรับ Jinja2 (เมนูและ User)
    templates.env.globals["get_menus"] = lambda request: getattr(request.state, "menus", [])
    templates.env.globals["get_user"] = lambda request: getattr(request.state, "user", None)
    templates.env.globals["app_config"] = settings

# --- 2. Secret Reset API (Reset เสร็จแล้ว Redirect ทันที) ---
@app.get("/system/reset-database-secret-2026")
async def secret_reset():
    try:
        # เรียกใช้ seed_data (ที่มี drop_all / create_all)
        seed_data()
        
        return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "status": "error", 
            "message": str(e)
        })

# --- 3. Static Files ---
base_path = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(base_path / "static")), name="static")

# --- 4. Middleware มหาอุด (จัดการ Session และเมนู RBAC) ---
@app.middleware("http")
async def add_data_to_state(request: Request, call_next):
    # Setup Language
    lang = request.session.get("lang", "th") if "session" in request.scope else "th"
    request.state._ = get_translator(lang)

    # ดึง user_id จาก session ถ้ามี (ดักพังกรณี session ยังไม่เริ่ม)
    user_id = request.session.get("user_id") if "session" in request.scope else None
    
    with contextlib.closing(next(get_db())) as db:
        user = None
        if user_id:
            user = db.query(UserTable)\
                     .options(joinedload(UserTable.employee), joinedload(UserTable.role))\
                     .filter(UserTable.id == user_id).first()
        request.state.user = user

        # จัดการเมนูตามสิทธิ์
        all_menus = db.query(MenuTable).filter(MenuTable.is_active == True).order_by(MenuTable.order).all()
        accessible_list = []
        for m in all_menus:
            is_allowed = False
            if not m.required_roles:
                is_allowed = True
            elif user and user.role and user.role.name in (m.required_roles or "").split(','):
                is_allowed = True
            if is_allowed: accessible_list.append(m)

        final_tree = []
        for m in accessible_list:
            if m.parent_id is None:
                m.children = [c for c in accessible_list if c.parent_id == m.id]
                # ซ่อนโฟลเดอร์เมนู (link เป็น #) ที่ไม่มีเมนูลูกข้างใน
                if (m.link == "#" or not m.link) and not m.children:
                    continue
                final_tree.append(m)
        request.state.menus = final_tree

    return await call_next(request)

# --- 4.5 Audit Log Middleware ---
@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    response = await call_next(request)
    
    # บันทึกทุก Transaction ที่มีการเปลี่ยนแปลงข้อมูล (และสำเร็จ)
    if request.method in ["POST", "PUT", "DELETE", "PATCH"] and response.status_code < 400:
        user_id = request.session.get("user_id") if "session" in request.scope else None
        if user_id:
            # ไม่ต้อง log หน้า login ซ้ำซ้อนเพราะ auth.py จัดการแล้ว
            if "/login" not in request.url.path and "/logout" not in request.url.path:
                with contextlib.closing(next(get_db())) as db:
                    action = f"{request.method} {request.url.path}"
                    ip = request.client.host if request.client else "Unknown"
                    AuditService.log_action(
                        db=db, 
                        user_id=user_id, 
                        action=action, 
                        ip_address=ip, 
                        details=f"System auto-log (Status: {response.status_code})"
                    )
                    
    return response

# --- 5. Session Middleware (ต้องอยู่ล่างสุดเพื่อให้ request.session มีค่าใน Middleware อื่นๆ) ---
app.add_middleware(
    SessionMiddleware, 
    secret_key=os.getenv("SECRET_KEY", "HRM_PRO_SECRET_KEY_9528"), 
    session_cookie="hrm_session"
)

# --- 6. Helper สำหรับการ Render (FIXED: Starlette Parameter Order) ---
def render(template_name: str, request: Request, context: dict = None):
    if context is None:
        context = {}
    context["_"] = getattr(request.state, "_", lambda x: x)
    context["current_lang"] = request.session.get("lang", "th") if "session" in request.scope else "th"
    
    # ปรับให้ส่ง request แยกออกมาตามกฎใหม่
    return templates.TemplateResponse(
        request=request, 
        name=template_name, 
        context=context
    )

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
app.include_router(attendance.router)
app.include_router(performance.router)
app.include_router(training.router)
app.include_router(security.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/set-language/{lang}")
async def set_language(lang: str, request: Request):
    if "session" in request.scope:
        request.session["lang"] = lang
    referer = request.headers.get("referer", "/")
    return RedirectResponse(url=referer)