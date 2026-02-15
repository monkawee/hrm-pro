from fastapi import Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    username = request.cookies.get("session_user")

    if not username:
        return None

    user = UserService.get_user_by_username(db, username)

    if not user:
        return None
        
    return user

async def admin_only(user=Depends(get_current_user)):
    if not user or user.role != "top_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="เฉพาะผู้ดูแลระบบเท่านั้นที่เข้าถึงหน้านี้ได้"
        )
    return user