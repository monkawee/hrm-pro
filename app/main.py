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

from fastapi import FastAPI, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import engine, Base, get_db
from app.models.user import UserTable, RoleTable
from app.services.user_service import UserService
from app.dependencies import get_current_user 

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)

# --- LOGIN / LOGOUT ---

@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = UserService.get_user_by_username(db, username)
    if user and UserService.verify_password(password, user.password):
        response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        response.set_cookie(key="session_user", value=user.username)
        return response
    return templates.TemplateResponse("login.html", {"request": request, "error": "Username หรือ Password ไม่ถูกต้อง"})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("session_user")
    return response

# --- DASHBOARD ---

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login?error=Session Expired")
    
    all_users = UserService.get_all_users(db)
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "user": user, 
        "total_employees": len(all_users)
    })

# --- EMPLOYEE ---

@app.get("/employees", response_class=HTMLResponse)
async def list_employees(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user:
        return RedirectResponse(url="/login?error=Please Login")
    employees = UserService.get_all_users(db)
    roles = db.query(RoleTable).all()
    managers = [u for u in employees if u.role in ["manager", "top_manager"]]
    
    return templates.TemplateResponse("employees.html", {
        "request": request,
        "employees": employees,
        "managers": managers,
        "user": user,
        "roles": roles
    })

@app.post("/employees/add")
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

@app.post("/employees/toggle/{user_id}")
async def toggle_employee(user_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user: return {"status": "error"}
    updated_user = UserService.toggle_status(db, user_id)
    return {"status": "success", "new_active_status": updated_user.is_active}

@app.post("/employees/delete/{user_id}")
async def delete_employee(user_id: int, db: Session = Depends(get_db), user = Depends(get_current_user)):
    if not user: return {"status": "error"}
    UserService.delete_user(db, user_id)
    return {"status": "success"}

@app.post("/employees/update/{user_id}")
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
        "manager_id": manager_id
    }
    
    user = UserService.update_user(db, user_id, update_data)
    if not user:
        return {"error": "User not found"}
        
    return {"message": "Update successful"}