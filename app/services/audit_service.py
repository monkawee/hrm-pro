from sqlalchemy.orm import Session
from app.models.audit import AuditLog

class AuditService:
    @staticmethod
    def log_action(db: Session, user_id: int, action: str, ip_address: str = None, details: str = None):
        """
        บันทึกประวัติการใช้งานระบบ (Audit Log)
        """
        log = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            details=details
        )
        db.add(log)
        db.commit()
