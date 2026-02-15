# 🚀 HRM PRO - Enterprise Employee Management

ระบบบริหารจัดการทรัพยากรบุคคล (HRM) ยุคใหม่ที่เน้นความเร็ว ความปลอดภัย และ UI ที่เป็นมิตรกับผู้ใช้งาน พัฒนาด้วย **FastAPI** และ **SQLAlchemy** พร้อมระบบฐานข้อมูลภายในตัว

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

## ✨ Highlight Features
- 🔐 **Secure Login:** ระบบยืนยันตัวตนพร้อมแบ่งระดับสิทธิ์ (Admin / Manager / User)
- 📊 **Dynamic Dashboard:** หน้าสรุปผลข้อมูลพนักงานแบบ Real-time พร้อม UI ทันสมัย
- 👥 **Employee Management:** ระบบจัดการสถานะพนักงาน (Toggle Active/Inactive)
- 🚀 **Offline-First Assets:** โหลดทรัพยากร (CSS/Fonts) จากเครื่อง 100% ไม่ต้องง้อเน็ตหน้างาน
- ⚡ **High Performance:** ขับเคลื่อนด้วย FastAPI สถาปัตยกรรมแบบ Asynchronous

## 🛠️ Tech Stack
- **Backend:** Python 3.8+ (FastAPI)
- **ORM:** SQLAlchemy (SQLite)
- **Frontend:** HTML5, Tailwind CSS (Standalone), FontAwesome 6
- **Template Engine:** Jinja2

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone [https://github.com/monkawee/hrm-pro.git](https://github.com/monkawee/hrm-pro.git)
cd hrm-pro
```

### 2. Setup Virtual Environment & Install Dependencies
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Install
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Data
```bash
python -m app.seed
```

### 4. Run the Server
```bash
uvicorn app.main:app --reload
```

เปิดบราวเซอร์ไปที่: http://127.0.0.1:8000

🔑 Demo Access
Username: admin

Password: 1234

🛤️ Roadmap

[x] Phase 1: Core System & Employee Management

[ ] Phase 2: Leave Request System (Coming Soon)

[ ] Phase 3: Payroll Automation

[ ] Phase 4: API Mobile Integration

Developed with ❤️ by monkawee
