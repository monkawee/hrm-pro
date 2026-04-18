# app/services/menu_service.py
from sqlalchemy.orm import Session
from app.models.menu import MenuTable

class MenuService:
    @staticmethod
    def get_all_menus(db: Session, include_inactive=True):
        query = db.query(MenuTable)
        if not include_inactive:
            query = query.filter(MenuTable.is_active == True)
        return query.order_by(MenuTable.order.asc()).all()

    @staticmethod
    def create_menu(db: Session, data: dict):
        last_menu = db.query(MenuTable).order_by(MenuTable.order.desc()).first()
        next_order = (last_menu.order + 1) if last_menu else 1
        
        new_menu = MenuTable(
            title=data['title'],
            link=data['link'],
            icon=data['icon'],
            order=next_order,
            required_roles=data.get('required_roles'),
            is_active=True
        )
        db.add(new_menu)
        db.commit()
        db.refresh(new_menu)
        return new_menu

    @staticmethod
    def update_menu(db: Session, menu_id: int, data: dict):
        menu = db.query(MenuTable).filter(MenuTable.id == menu_id).first()
        if menu:
            menu.title = data.get('title', menu.title)
            menu.link = data.get('link', menu.link)
            menu.icon = data.get('icon', menu.icon)
            menu.required_roles = data.get('required_roles') # รับมาเป็น string "admin,manager"
            menu.is_active = data.get('is_active', menu.is_active)
            db.commit()
            db.refresh(menu)
        return menu

    @staticmethod
    def delete_menu(db: Session, menu_id: int):
        menu = db.query(MenuTable).filter(MenuTable.id == menu_id).first()
        if menu:
            db.delete(menu)
            db.commit()
            return True
        return False

    @staticmethod
    def update_menu_order(db: Session, order_list: list):
        """
        อัปเดตลำดับเมนู (รับค่าเป็น List ของ ID เช่น [3, 1, 2])
        """
        try:
            for index, menu_id in enumerate(order_list):
                menu = db.query(MenuTable).filter(MenuTable.id == menu_id).first()
                if menu:
                    menu.order = index + 1  # ให้ลำดับเริ่มที่ 1, 2, 3...
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error updating menu order: {e}")
            return False