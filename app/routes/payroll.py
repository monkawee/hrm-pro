from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import UserTable
from app.models.employee import Employee
from app.models.payroll import Payroll, PayrollStatus
from app.core.config import templates
from datetime import datetime

router = APIRouter(tags=["Payroll"], prefix="/payroll")

@router.get("", response_class=HTMLResponse)
async def payroll_list(
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
        
    role_name = user.role.name if user.role else "employee"
    
    if role_name in ["hr", "top_manager"]:
        payrolls = db.query(Payroll).order_by(Payroll.year.desc(), Payroll.month.desc(), Payroll.created_at.desc()).all()
    else:
        if user.employee:
            payrolls = db.query(Payroll).filter(
                Payroll.employee_id == user.employee.id
            ).order_by(Payroll.year.desc(), Payroll.month.desc(), Payroll.created_at.desc()).all()
        else:
            payrolls = []

    return templates.TemplateResponse("payroll/index.html", {
        "request": request,
        "user": user,
        "payrolls": payrolls,
        "PayrollStatus": PayrollStatus
    })

@router.post("/generate")
async def generate_payroll(
    request: Request,
    month: int = Form(...),
    year: int = Form(...),
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or user.role.name not in ["hr", "top_manager"]:
        return RedirectResponse(url="/payroll")
        
    # Get all active employees
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    
    for emp in employees:
        # Check if payroll already exists for this month/year
        existing = db.query(Payroll).filter(
            Payroll.employee_id == emp.id,
            Payroll.month == month,
            Payroll.year == year
        ).first()
        
        if not existing:
            # Generate mock deductions
            deductions = int(emp.base_salary * 0.05) if emp.base_salary else 0 # e.g. 5% tax/social security
            net_salary = emp.base_salary - deductions if emp.base_salary else 0
            
            new_payroll = Payroll(
                employee_id=emp.id,
                month=month,
                year=year,
                basic_salary=emp.base_salary or 0,
                deductions=deductions,
                net_salary=net_salary,
                status=PayrollStatus.PENDING
            )
            db.add(new_payroll)
            
    db.commit()
    return RedirectResponse(url="/payroll", status_code=303)

@router.get("/{payroll_id}/slip", response_class=HTMLResponse)
async def view_slip(
    payroll_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
        
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        return RedirectResponse(url="/payroll")
        
    role_name = user.role.name if user.role else "employee"
    if role_name not in ["hr", "top_manager"] and payroll.employee_id != user.employee.id:
        return RedirectResponse(url="/payroll")

    return templates.TemplateResponse("payroll/slip.html", {
        "request": request,
        "user": user,
        "payroll": payroll,
        "PayrollStatus": PayrollStatus
    })

@router.post("/{payroll_id}/status")
async def update_payroll_status(
    payroll_id: int,
    status: str = Form(...),
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or user.role.name not in ["hr", "top_manager"]:
        return RedirectResponse(url="/payroll")
        
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if payroll:
        payroll.status = PayrollStatus(status)
        if payroll.status == PayrollStatus.PAID:
            payroll.payment_date = datetime.now()
        db.commit()
        
    return RedirectResponse(url="/payroll", status_code=303)
