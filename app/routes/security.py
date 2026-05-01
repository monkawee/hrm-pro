from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import UserTable
from app.models.audit import AuditLog
from app.core.config import templates
from datetime import datetime
from app.services.audit_service import AuditService
import os

router = APIRouter(tags=["Security"], prefix="/security")

@router.post("/pdpa/accept")
async def accept_pdpa(
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if user:
        user.pdpa_consented_at = datetime.now()
        db.commit()
        AuditService.log_action(db, user.id, "ACCEPT_PDPA", request.client.host)
        
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/audit", response_class=HTMLResponse)
async def audit_logs_view(
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or user.role.name != "top_manager":
        return RedirectResponse(url="/dashboard")
        
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(200).all()
    
    return templates.TemplateResponse("security/audit.html", {
        "request": request,
        "user": user,
        "logs": logs
    })

@router.get("/backup")
async def download_backup(
    request: Request,
    user: UserTable = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not user or user.role.name != "top_manager":
        return RedirectResponse(url="/dashboard")
        
    AuditService.log_action(db, user.id, "DOWNLOAD_DB_BACKUP", request.client.host)
    
    db_path = "hrm.db"
    if os.path.exists(db_path):
        return FileResponse(db_path, media_type='application/octet-stream', filename=f"hrm_backup_{datetime.now().strftime('%Y%m%d')}.db")
    
    return RedirectResponse(url="/dashboard")
