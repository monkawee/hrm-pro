from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import UserTable
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest, LeaveType, LeaveStatus
from app.core.config import templates
from datetime import datetime

router = APIRouter(tags=["Leave"], prefix="/leaves")

@router.get("", response_class=HTMLResponse)
async def leave_list(
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
        
    role_name = user.role.name if user.role else "employee"
    
    # HR and Top Manager can see all
    if role_name in ["hr", "top_manager"]:
        leaves = db.query(LeaveRequest).order_by(LeaveRequest.created_at.desc()).all()
    # Manager can see their own and their subordinates'
    elif role_name == "manager" and user.employee:
        subordinate_ids = [sub.id for sub in user.employee.subordinates]
        leaves = db.query(LeaveRequest).filter(
            (LeaveRequest.employee_id == user.employee.id) | 
            (LeaveRequest.employee_id.in_(subordinate_ids))
        ).order_by(LeaveRequest.created_at.desc()).all()
    # Employee can only see their own
    else:
        if user.employee:
            leaves = db.query(LeaveRequest).filter(
                LeaveRequest.employee_id == user.employee.id
            ).order_by(LeaveRequest.created_at.desc()).all()
        else:
            leaves = []

    # return templates.TemplateResponse("leave/index.html", {
    #     "request": request,
    #     "user": user,
    #     "leaves": leaves,
    #     "LeaveStatus": LeaveStatus,
    #     "LeaveType": LeaveType
    # })
    return templates.TemplateResponse(
        request=request, 
        name="leave/index.html", 
        context={
            "user": user,
            "leaves": leaves,
            "LeaveStatus": LeaveStatus,
            "LeaveType": LeaveType
        }
    )   

@router.get("/request", response_class=HTMLResponse)
async def leave_request_form(
    request: Request,
    user: UserTable = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
        
    if not user.employee:
        # Cannot request leave if not an employee
        return RedirectResponse(url="/leaves")

    # return templates.TemplateResponse("leave/form.html", {
    #     "request": request,
    #     "user": user,
    #     "LeaveType": LeaveType
    # })
    return templates.TemplateResponse(
        request=request, 
        name="leave/form.html", 
        context={
            "user": user,
            "LeaveType": LeaveType
        }
    )

@router.post("/request")
async def submit_leave_request(
    request: Request,
    leave_type: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    reason: str = Form(...),
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or not user.employee:
        return RedirectResponse(url="/login")
        
    new_leave = LeaveRequest(
        employee_id=user.employee.id,
        leave_type=LeaveType(leave_type),
        start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
        end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
        reason=reason,
        status=LeaveStatus.PENDING
    )
    
    db.add(new_leave)
    db.commit()
    
    return RedirectResponse(url="/leaves", status_code=303)

@router.post("/{leave_id}/status")
async def update_leave_status(
    leave_id: int,
    status: str = Form(...),
    manager_comment: str = Form(None),
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")
        
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        return RedirectResponse(url="/leaves")
        
    role_name = user.role.name if user.role else "employee"
    
    # Check permissions
    can_update = False
    if role_name in ["hr", "top_manager"]:
        can_update = True
    elif role_name == "manager" and user.employee:
        subordinate_ids = [sub.id for sub in user.employee.subordinates]
        if leave.employee_id in subordinate_ids:
            can_update = True
            
    if can_update:
        leave.status = LeaveStatus(status)
        if manager_comment:
            leave.manager_comment = manager_comment
        db.commit()
        
    return RedirectResponse(url="/leaves", status_code=303)
