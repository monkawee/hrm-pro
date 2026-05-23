# app/routes/auth.py
from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.services.user_service import UserService
from app.services.audit_service import AuditService
from app.core.config import settings, templates

router = APIRouter()

@router.get("/login/bypass/{username}")
async def bypass_login(request: Request, username: str, db: Session = Depends(get_db)):
    if settings.ENVIRONMENT == "production":
        return RedirectResponse(url="/login")
        
    user = UserService.get_user_by_username(db, username)
    if user:
        request.session["user_id"] = user.id 
        AuditService.log_action(db, user.id, "LOGIN_BYPASS", request.client.host)
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse(url="/login")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={"error": error}
    )

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = UserService.get_user_by_username(db, username)
    if user and UserService.verify_password(password, user.password):
        request.session["user_id"] = user.id 
        AuditService.log_action(db, user.id, "LOGIN", request.client.host)
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request, 
        name="login.html", 
        context={
            "error": "Username หรือ Password ไม่ถูกต้อง"
        }
    )

@router.get("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if user_id:
        AuditService.log_action(db, user_id, "LOGOUT", request.client.host)
    request.session.clear() 
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)