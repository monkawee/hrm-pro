from datetime import datetime, time, date, timedelta
from app.models.attendance import AttendanceRecord, AttendanceStatus, Shift

class AttendanceService:
    @staticmethod
    def calculate_status(shift: Shift, time_in: time) -> AttendanceStatus:
        """
        คำนวณสถานะการมาทำงาน (ตรงเวลา, สาย)
        """
        if not time_in:
            return AttendanceStatus.ABSENT
            
        # สร้าง datetime เพื่อนำมาคำนวณบวก/ลบเวลาได้
        dummy_date = date.today()
        shift_start = datetime.combine(dummy_date, shift.start_time)
        actual_in = datetime.combine(dummy_date, time_in)
        
        # บวก Grace Period
        allowed_in = shift_start + timedelta(minutes=shift.late_grace_period)
        
        if actual_in > allowed_in:
            return AttendanceStatus.LATE
        return AttendanceStatus.PRESENT

    @staticmethod
    def calculate_hours(shift: Shift, time_in: time, time_out: time):
        """
        คำนวณชั่วโมงทำงานรวม และ OT (หากมี)
        คืนค่าเป็น (total_work_hours, ot_hours)
        """
        if not time_in or not time_out:
            return 0.0, 0.0
            
        dummy_date = date.today()
        in_dt = datetime.combine(dummy_date, time_in)
        out_dt = datetime.combine(dummy_date, time_out)
        
        # เผื่อกรณีเข้ากะดึก ข้ามวัน
        if out_dt < in_dt:
            out_dt += timedelta(days=1)
            
        total_worked = (out_dt - in_dt).total_seconds() / 3600.0
        
        # คำนวณชั่วโมงทำงานปกติตามกะ (หักพัก 1 ชั่วโมงโดยประมาณ)
        shift_start_dt = datetime.combine(dummy_date, shift.start_time)
        shift_end_dt = datetime.combine(dummy_date, shift.end_time)
        if shift_end_dt < shift_start_dt:
            shift_end_dt += timedelta(days=1)
            
        normal_hours = (shift_end_dt - shift_start_dt).total_seconds() / 3600.0 - 1.0 # สมมติว่าพัก 1 ชม.
        if normal_hours < 0: normal_hours = 0
        
        # ลบเวลาพักเที่ยง 1 ชม. ออกจากเวลาทำงานจริง (ถ้าทำเกิน 4 ชม.)
        if total_worked > 4.0:
            total_worked -= 1.0
            
        ot_hours = 0.0
        if total_worked > normal_hours:
            ot_hours = total_worked - normal_hours
            total_worked = normal_hours # เวลาทำงานปกติไม่เกินกะ
            
        return round(total_worked, 2), round(ot_hours, 2)
