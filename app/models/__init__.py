# app/models/__init__.py
from .role import RoleTable
from .menu import MenuTable
from .employee import Employee, Attachment # Import ตัวนี้ก่อนหรือหลังก็ได้
from .user import UserTable                # แต่ต้องมีให้ครบที่นี่