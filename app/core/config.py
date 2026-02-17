# app/core/config.py
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")

templates.env.globals.update({
    "get_menus": lambda request: getattr(request.state, "menus", []),
    "get_user": lambda request: getattr(request.state, "user", None)
})

class Settings:
    PROJECT_NAME: str = "HRM Pro" # บอสเปลี่ยนชื่อที่นี่ที่เดียว จบเลย!
    PROJECT_LOGO: str = ""           # ถ้าใส่ path เช่น "/static/img/logo.png" จะโชว์รูป

settings = Settings()