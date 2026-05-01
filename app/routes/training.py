from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import UserTable
from app.models.training import TrainingCourse, TrainingRecord, TrainingStatus
from app.core.config import templates
from datetime import datetime
from app.services.audit_service import AuditService

router = APIRouter(tags=["Training"], prefix="/training")

@router.get("", response_class=HTMLResponse)
async def training_list(
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
        
    courses = db.query(TrainingCourse).all()
    
    if user.role and user.role.name in ["hr", "top_manager"]:
        records = db.query(TrainingRecord).all()
    else:
        if user.employee:
            records = db.query(TrainingRecord).filter(TrainingRecord.employee_id == user.employee.id).all()
        else:
            records = []

    return templates.TemplateResponse("training/index.html", {
        "request": request,
        "user": user,
        "courses": courses,
        "records": records,
        "TrainingStatus": TrainingStatus,
        "today": datetime.now().date()
    })

@router.post("/enroll")
async def enroll_course(
    request: Request,
    course_id: int = Form(...),
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or not user.employee:
        return RedirectResponse(url="/login")
        
    existing = db.query(TrainingRecord).filter(
        TrainingRecord.employee_id == user.employee.id,
        TrainingRecord.course_id == course_id
    ).first()
    
    if not existing:
        new_record = TrainingRecord(
            employee_id=user.employee.id,
            course_id=course_id,
            status=TrainingStatus.ENROLLED
        )
        db.add(new_record)
        db.commit()
        AuditService.log_action(db, user.id, f"ENROLL_COURSE_{course_id}", request.client.host)
        
    return RedirectResponse(url="/training", status_code=303)
