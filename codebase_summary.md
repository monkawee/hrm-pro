# HRM Pro - Codebase Summary (Agent's Perspective)

นี่คือบทสรุปโครงสร้างของโปรเจกต์ **HRM Pro** จากการสำรวจ Source Code ทั้งหมด เพื่อให้เข้าใจสถาปัตยกรรมและพร้อมสำหรับการพัฒนาต่อในอนาคต

## 🛠 Tech Stack
- **Backend Framework**: FastAPI (Python) ขับเคลื่อนด้วยสถาปัตยกรรม Asynchronous
- **Database / ORM**: SQLite + SQLAlchemy (จัดการผ่าน `app.core.database`)
- **Frontend / UI**: HTML5 + Jinja2 Templates (`app.templates`) และจัดการสไตล์ด้วย Tailwind CSS
- **Authentication**: Session-based Authentication (`SessionMiddleware` จาก `starlette`)

## 📂 Project Structure & Architecture
โปรเจกต์ใช้โครงสร้างแบบ Modular/MVC-like ซึ่งแบ่งแยกความรับผิดชอบ (Separation of Concerns) อย่างชัดเจน:

- **`app/main.py`**: Entry Point ของแอปพลิเคชัน
  - ทำการ Mount Static files
  - Register Routes ต่างๆ (Dashboard, Auth, User, Role, Menu, Employee)
  - จัดการ **Global Middleware** ที่สำคัญมาก (ดูเพิ่มเติมในส่วน *Core Mechanisms*)
- **`app/models/`**: นิยามโครงสร้างฐานข้อมูล (SQLAlchemy Declarative Models)
  - `user.py`, `role.py`, `menu.py`, `employee.py`
  - มีการทำ Relationships เชื่อมโยงหากัน (เช่น User กับ Employee, User กับ Role)
- **`app/routes/`**: เสมือน Controller จัดการ API endpoints และ Web Routes ควบคุม Business Logic และการเรียก Template
- **`app/core/`**: การตั้งค่าหลักของระบบ
  - `config.py` (ตั้งค่าตัวแปรระบบ)
  - `database.py` (เชื่อมต่อและ Session ของ DB)
  - `security.py` (ระบบความปลอดภัย เช่น Hashing รหัสผ่าน ถ้ามี)
- **`app/templates/`**: ไฟล์ `.html` (Jinja2) สำหรับการแสดงผล UI แบ่งเป็น Layouts หลักและหน้าย่อยต่างๆ ตาม Modules

## ⚙️ Core Mechanisms (กลไกหลักที่สำคัญ)

### 1. Authentication & RBAC (Role-Based Access Control)
- **Session Auth**: เมื่อผู้ใช้ Login ผ่าน `/login` (ใน `auth.py`) ระบบจะเก็บ `user_id` ลงใน Session Cookie (`hrm_session`)
- **Global Data Middleware (`add_data_to_state`)**:
  - ทุกๆ HTTP Request จะวิ่งผ่าน Middleware นี้ใน `main.py`
  - หน้าที่หลักคือเช็ก Session ว่าใครกำลัง Login อยู่ และดึงข้อมูล User พร้อม Employee/Role ผ่าน `joinedload` เพื่อลดรอบคิวรีฐานข้อมูล (N+1 Problem) แล้วนำไปฝากไว้ใน `request.state.user`
  - สร้าง **Dynamic Menu Tree** ตามสิทธิ์การใช้งาน (Roles) ของ User นั้นๆ และผูกลูกเมนูเข้ากับเมนูแม่ แล้วฝากไว้ใน `request.state.menus`

### 2. Template Context Injection
ใน `startup_event` ของ FastAPI ระบบได้ฝากฟังก์ชันเข้าไปในระดับ Global ของ Jinja2 Templates:
- `get_menus(request)`: ใช้สำหรับวาด Sidebar Menu
- `get_user(request)`: ใช้ดึงข้อมูลผู้ใช้ปัจจุบันไปแสดงผลตามจุดต่างๆ (เช่น Header)
- ทำให้ไม่ต้องส่ง `user` หรือ `menus` ซ้ำๆ ทุกครั้งเวลาทำ `render()` ในระดับ Route

### 3. Database Session Management
- ใช้ Dependency Injection (`get_db`) สำหรับส่งต่อ DB Session เข้าไปในแต่ละ Endpoint และปิด Session อัตโนมัติเมื่อ Request สิ้นสุด

## 🚀 สรุปสำหรับ Agent
โปรเจกต์นี้เป็น **FastAPI Monolith** ที่มีโครงสร้างแข็งแรงและเรียบง่าย
- หากต้องการ **เพิ่มหน้าใหม่/ฟีเจอร์ใหม่**: 
  1. สร้าง Model (ถ้าต้องเก็บข้อมูลใหม่)
  2. เพิ่ม Route ใน `app/routes/` 
  3. ผูก Route เข้า `main.py`
  4. สร้าง Template UI ใน `app/templates/`
  5. ไปตั้งค่าสิทธิ์และ Sidebar ในฐานข้อมูล `MenuTable`
- **ข้อควรระวัง**: การจัดการ State (เช่น การส่งข้อมูลผู้ใช้ให้ Frontend) จัดการผ่าน `request.state` และ Middleware เรียบร้อยแล้ว ไม่ต้องทำซ้ำใน Route
