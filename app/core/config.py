# app/core/config.py
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")

templates.env.globals.update({
    "get_menus": lambda request: getattr(request.state, "menus", []),
    "get_user": lambda request: getattr(request.state, "user", None)
})