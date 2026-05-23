from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse # เพิ่ม RedirectResponse เผื่อไว้
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.employee import Employee
from app.models.user import UserTable
from app.core.config import templates

# 🌟 บรรทัดนี้แหละตัวดี เช็กว่าสะกด 'router' ถูกไหม (ไม่มี s นะครับ)
router = APIRouter(tags=["Dashboard"]) 

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request, 
    db: Session = Depends(get_db), 
    user = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/login")

    my_subordinates = 0
    if user.employee:
        my_subordinates = db.query(Employee).filter(Employee.manager_id == user.employee.id).count()

    # ดึงข้อมูลจริงจาก DB
    stats = {
        "total_employees": db.query(Employee).count(),
        "total_users": db.query(UserTable).count(),
        "active_employees": db.query(Employee).filter(Employee.is_active == True).count(),
        "my_subordinates": my_subordinates,
    }
    
    recent_employees = db.query(Employee).order_by(Employee.id.desc()).limit(5).all()

    # return templates.TemplateResponse("dashboard.html", {
    #     "request": request,
    #     "user": user,
    #     "stats": stats,
    #     "recent_employees": recent_employees
    # })
    return templates.TemplateResponse(
        request=request, 
        name="dashboard.html", 
        context={
            "user": user,
            "stats": stats,
            "recent_employees": recent_employees
        }
    )