# app/core/config.py
from fastapi.templating import Jinja2Templates
from fastapi import Request
from jinja2 import pass_context

templates = Jinja2Templates(directory="app/templates")

@pass_context
def translate(context, text):
    request = context.get("request")
    if request and hasattr(request.state, "_"):
        return request.state._(text)
    return text

templates.env.globals.update({
    "get_menus": lambda request: getattr(request.state, "menus", []),
    "get_user": lambda request: getattr(request.state, "user", None),
    "_": translate
})

import os

class Settings:
    PROJECT_NAME: str = "HRM Pro" # บอสเปลี่ยนชื่อที่นี่ที่เดียว จบเลย!
    PROJECT_LOGO: str = ""           # ถ้าใส่ path เช่น "/static/img/logo.png" จะโชว์รูป
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development") # check 'production' to disable bypass

settings = Settings()