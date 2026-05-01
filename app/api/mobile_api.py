from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

from app.core.database import get_db
from app.models.user import UserTable
from app.models.employee import Employee
from app.models.leave_request import LeaveRequest
from app.models.payroll import Payroll

router = APIRouter(tags=["Mobile API"], prefix="/api/mobile")

# --- Schemas ---
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    role: str
    employee_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# --- Routes ---
@router.post("/login", response_model=UserResponse)
def mobile_login(credentials: LoginRequest, db: Session = Depends(get_db)):
    # Simple auth for demonstration purposes (matching auth.py)
    user = db.query(UserTable).filter(UserTable.username == credentials.username).first()
    
    if not user or user.password != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")

    return UserResponse(
        user_id=user.id,
        username=user.username,
        role=user.role.name if user.role else "employee",
        employee_id=user.employee.id if user.employee else None,
        first_name=user.employee.first_name if user.employee else None,
        last_name=user.employee.last_name if user.employee else None
    )

@router.get("/profile")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    # Typically user_id would come from a token, but we use query param for simplicity in Phase 4
    user = db.query(UserTable).filter(UserTable.id == user_id).first()
    if not user or not user.employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
        
    emp = user.employee
    return {
        "employee_code": emp.employee_code,
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "join_date": emp.join_date,
        "base_salary": emp.base_salary
    }

@router.get("/leaves")
def get_leaves(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserTable).filter(UserTable.id == user_id).first()
    if not user or not user.employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
        
    leaves = db.query(LeaveRequest).filter(LeaveRequest.employee_id == user.employee.id).order_by(LeaveRequest.created_at.desc()).all()
    
    result = []
    for l in leaves:
        result.append({
            "id": l.id,
            "leave_type": l.leave_type.value,
            "start_date": l.start_date,
            "end_date": l.end_date,
            "reason": l.reason,
            "status": l.status.value,
            "manager_comment": l.manager_comment
        })
    return result

@router.get("/payslips")
def get_payslips(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserTable).filter(UserTable.id == user_id).first()
    if not user or not user.employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
        
    payrolls = db.query(Payroll).filter(Payroll.employee_id == user.employee.id).order_by(Payroll.year.desc(), Payroll.month.desc()).all()
    
    result = []
    for p in payrolls:
        result.append({
            "id": p.id,
            "month": p.month,
            "year": p.year,
            "basic_salary": p.basic_salary,
            "deductions": p.deductions,
            "net_salary": p.net_salary,
            "status": p.status.value,
            "payment_date": p.payment_date
        })
    return result
