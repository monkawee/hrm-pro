from fastapi import FastAPI, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional

# นำเข้าส่วนประกอบที่เราสร้างไว้ (เช็คชื่อโฟลเดอร์ให้ดีนะครับ)
from app.core.database import engine, Base, get_db
from app.models.user import UserTable, UserRole


# 1. ประกาศตัวแปร app ก่อน (สำคัญมาก!)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. ตั้งค่า Template และ Static files
templates = Jinja2Templates(directory="app/templates")

# 3. สร้าง Table ใน Database (ถ้ายังไม่มี)
Base.metadata.create_all(bind=engine)

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # ค้นหา User จาก DB จริง
    user = db.query(UserTable).filter(UserTable.username == username).first()
    
    if not user or user.password != password:
        return RedirectResponse(url="/?error=Invalid credentials", status_code=status.HTTP_303_SEE_OTHER)
    
    if not user.is_active:
        return RedirectResponse(url="/?error=Account disabled", status_code=status.HTTP_303_SEE_OTHER)

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="session_user", value=username)
    return response

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("session_user")
    user = db.query(UserTable).filter(UserTable.username == username).first()
    
    if not user:
        return RedirectResponse(url="/?error=Please login")
        
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

@app.get("/employees", response_class=HTMLResponse)
async def list_employees(request: Request, db: Session = Depends(get_db)):
    employees = db.query(UserTable).all()
    return templates.TemplateResponse("employees.html", {"request": request, "employees": employees})

@app.post("/employees/toggle/{user_id}")
async def toggle_user_status(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserTable).filter(UserTable.id == user_id).first()
    if user:
        user.is_active = not user.is_active
        db.commit()
    return RedirectResponse(url="/employees", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout(request: Request):
    response = templates.TemplateResponse("logout.html", {"request": request})
    response.delete_cookie("session_user") # ลบ Cookie ทิ้ง
    return response

@app.exception_handler(404)
async def custom_404_handler(request: Request, __):
    return templates.TemplateResponse("under_construction.html", {"request": request}, status_code=404)