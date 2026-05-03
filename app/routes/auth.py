# app/routes/auth.py
from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from fastapi.templating import Jinja2Templates

from app.core.database import get_db
from app.services.user_service import UserService

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse(request=request,name="login.html",context={"error": error})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = UserService.get_user_by_username(db, username)
    if user and UserService.verify_password(password, user.password):
        # 🌟 1. เก็บ ID ลง Session (Middleware จะจัดการเรื่อง Cookie ให้เองแบบปลอดภัย)
        request.session["user_id"] = user.id 
        
        # 🌟 2. Redirect ไป Dashboard ด้วย 303
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
        
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "error": "Username หรือ Password ไม่ถูกต้อง"
    })

@router.get("/logout")
async def logout(request: Request): # เพิ่ม request เข้ามาด้วย
    # 🌟 3. ล้าง Session ทิ้งให้หมด
    request.session.clear() 
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)