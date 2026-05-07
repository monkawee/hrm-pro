from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import UserTable
from app.models.employee import Employee
from app.models.performance import PerformanceReview, ReviewStatus
from app.core.config import templates
from datetime import datetime
from app.services.audit_service import AuditService

router = APIRouter(tags=["Performance"], prefix="/performance")

@router.get("", response_class=HTMLResponse)
async def performance_list(
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
        
    role_name = user.role.name if user.role else "employee"
    
    if role_name in ["hr", "top_manager", "manager"]:
        reviews = db.query(PerformanceReview).order_by(PerformanceReview.year.desc(), PerformanceReview.quarter.desc()).all()
    else:
        if user.employee:
            reviews = db.query(PerformanceReview).filter(PerformanceReview.employee_id == user.employee.id).all()
        else:
            reviews = []

    # return templates.TemplateResponse("performance/index.html", {
    #     "request": request,
    #     "user": user,
    #     "reviews": reviews,
    #     "ReviewStatus": ReviewStatus
    # })
    return templates.TemplateResponse(
        request=request, 
        name="performance/index.html", 
        context={
            "user": user,
            "reviews": reviews,
            "ReviewStatus": ReviewStatus
        }
    )

@router.get("/evaluate", response_class=HTMLResponse)
async def evaluate_view(
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or user.role.name not in ["hr", "top_manager", "manager"]:
        return RedirectResponse(url="/performance")
        
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    # return templates.TemplateResponse("performance/evaluate.html", {
    #     "request": request,
    #     "user": user,
    #     "employees": employees
    # })
    return templates.TemplateResponse(
        request=request, 
        name="performance/evaluate.html", 
        context={
            "user": user,
            "employees": employees
        }
    )

@router.post("/evaluate")
async def evaluate_action(
    request: Request,
    employee_id: int = Form(...),
    year: int = Form(...),
    quarter: int = Form(...),
    kpi_score: float = Form(...),
    feedback: str = Form(""),
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or user.role.name not in ["hr", "top_manager", "manager"]:
        return RedirectResponse(url="/performance")
        
    existing = db.query(PerformanceReview).filter(
        PerformanceReview.employee_id == employee_id,
        PerformanceReview.year == year,
        PerformanceReview.quarter == quarter
    ).first()
    
    if existing:
        existing.kpi_score = kpi_score
        existing.feedback = feedback
        existing.reviewer_id = user.id
    else:
        new_review = PerformanceReview(
            employee_id=employee_id,
            reviewer_id=user.id,
            year=year,
            quarter=quarter,
            kpi_score=kpi_score,
            feedback=feedback,
            status=ReviewStatus.SUBMITTED
        )
        db.add(new_review)
        
    db.commit()
    AuditService.log_action(db, user.id, f"EVALUATE_PERFORMANCE_EMP_{employee_id}", request.client.host)
    
    return RedirectResponse(url="/performance", status_code=303)
