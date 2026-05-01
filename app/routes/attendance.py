from fastapi import APIRouter, Depends, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, date
import csv
import io

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.user import UserTable
from app.models.attendance import AttendanceRecord, Shift, AttendanceStatus
from app.services.attendance_service import AttendanceService
from app.core.config import templates

router = APIRouter(tags=["Attendance"], prefix="/attendance")

@router.get("/check", response_class=HTMLResponse)
async def check_view(
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or not user.employee:
        return RedirectResponse(url="/login")
        
    today = date.today()
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == user.employee.id,
        AttendanceRecord.date == today
    ).first()
    
    return templates.TemplateResponse("attendance/check.html", {
        "request": request,
        "user": user,
        "record": record
    })

@router.post("/action")
async def check_action(
    request: Request,
    lat: float = Form(0.0),
    lng: float = Form(0.0),
    action: str = Form(...), # "in" or "out"
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or not user.employee:
        return RedirectResponse(url="/login")
        
    today = date.today()
    now_time = datetime.now().time()
    
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == user.employee.id,
        AttendanceRecord.date == today
    ).first()
    
    # ดึงกะการทำงาน (สมมติว่ามีแค่กะเดียวในตอนนี้ หรือดึงกะแรกมาใช้ก่อน)
    shift = db.query(Shift).first()
    if not shift:
        # Fallback สร้างกะจำลอง
        shift = Shift(name="Default", start_time=datetime.strptime("09:00", "%H:%M").time(), end_time=datetime.strptime("18:00", "%H:%M").time())
        db.add(shift)
        db.commit()
        db.refresh(shift)
        
    if action == "in":
        if not record:
            status = AttendanceService.calculate_status(shift, now_time)
            record = AttendanceRecord(
                employee_id=user.employee.id,
                shift_id=shift.id,
                date=today,
                time_in=now_time,
                in_location_lat=lat,
                in_location_lng=lng,
                status=status
            )
            db.add(record)
    elif action == "out":
        if record and not record.time_out:
            record.time_out = now_time
            record.out_location_lat = lat
            record.out_location_lng = lng
            
            # คำนวณชั่วโมง
            t_work, t_ot = AttendanceService.calculate_hours(shift, record.time_in, record.time_out)
            record.total_work_hours = t_work
            record.ot_hours = t_ot
            
    db.commit()
    return RedirectResponse(url="/attendance/check", status_code=303)

@router.get("/history", response_class=HTMLResponse)
async def history_view(
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or not user.employee:
        return RedirectResponse(url="/login")
        
    records = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == user.employee.id
    ).order_by(AttendanceRecord.date.desc()).all()
    
    return templates.TemplateResponse("attendance/history.html", {
        "request": request,
        "user": user,
        "records": records,
        "AttendanceStatus": AttendanceStatus
    })

@router.get("/report", response_class=HTMLResponse)
async def report_view(
    request: Request,
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or user.role.name not in ["hr", "top_manager"]:
        return RedirectResponse(url="/dashboard")
        
    records = db.query(AttendanceRecord).order_by(AttendanceRecord.date.desc()).all()
    
    return templates.TemplateResponse("attendance/report.html", {
        "request": request,
        "user": user,
        "records": records,
        "AttendanceStatus": AttendanceStatus
    })

@router.get("/export")
async def export_csv(
    db: Session = Depends(get_db),
    user: UserTable = Depends(get_current_user)
):
    if not user or user.role.name not in ["hr", "top_manager"]:
        return RedirectResponse(url="/dashboard")
        
    records = db.query(AttendanceRecord).order_by(AttendanceRecord.date.desc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Employee ID', 'Name', 'Time In', 'Time Out', 'Status', 'Work Hours', 'OT Hours'])
    
    for r in records:
        writer.writerow([
            r.date,
            r.employee.employee_code,
            f"{r.employee.first_name} {r.employee.last_name}",
            r.time_in.strftime('%H:%M') if r.time_in else '-',
            r.time_out.strftime('%H:%M') if r.time_out else '-',
            r.status.value,
            r.total_work_hours,
            r.ot_hours
        ])
        
    output.seek(0)
    response = StreamingResponse(output, media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=attendance_report.csv"
    return response
