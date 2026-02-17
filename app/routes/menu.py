from fastapi import APIRouter, Depends, Request, Form, status, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.core.database import get_db
from app.services.menu_service import MenuService
from app.services.role_service import RoleService
from app.core.config import templates
from app.dependencies import get_current_user
from app.models.menu import MenuTable

router = APIRouter(prefix="/menus", tags=["Menus"])

class OrderUpdate(BaseModel):
    order_list: List[int]

@router.get("/", response_class=HTMLResponse)
async def list_menus(request: Request, db: Session = Depends(get_db), user = Depends(get_current_user)):
    menus_list = MenuService.get_all_menus(db)
    roles = RoleService.get_all_roles(db, only_active=True)
    
    return templates.TemplateResponse("menus/menus.html", {
        "request": request,
        "menus_list": menus_list,
        "roles": roles,
        "user": user
    })

@router.post("/add")
async def add_menu(
    title: str = Form(...),
    link: str = Form(...),
    icon: str = Form(...),
    roles: List[str] = Form(None), # รับค่า checkbox ชื่อเดียวกันเป็น list
    db: Session = Depends(get_db)
):
    required_roles = ",".join(roles) if roles else None
    MenuService.create_menu(db, {
        "title": title, 
        "link": link, 
        "icon": icon, 
        "required_roles": required_roles
    })
    return RedirectResponse(url="/menus", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/update/{menu_id}")
async def update_menu(
    menu_id: int,
    title: str = Form(...),
    link: str = Form(...),
    icon: str = Form(...),
    is_active: str = Form("false"),
    roles: List[str] = Form(None),
    db: Session = Depends(get_db)
):
    required_roles = ",".join(roles) if roles else None
    active_bool = True if is_active.lower() == "true" else False
    
    MenuService.update_menu(db, menu_id, {
        "title": title,
        "link": link,
        "icon": icon,
        "is_active": active_bool,
        "required_roles": required_roles
    })
    return {"status": "success"}

@router.post("/reorder")
async def reorder_menus(data: OrderUpdate, db: Session = Depends(get_db)):
    for index, menu_id in enumerate(data.order_list):
        menu = db.query(MenuTable).filter(MenuTable.id == menu_id).first()
        if menu:
            menu.order = index + 1
    db.commit()
    return {"status": "success", "message": "Reordered successfully"}

@router.post("/delete/{menu_id}")
async def delete_menu(menu_id: int, db: Session = Depends(get_db)):
    success = MenuService.delete_menu(db, menu_id)
    if success:
        return {"status": "success"}
    return {"status": "error", "message": "Menu not found"}, 404