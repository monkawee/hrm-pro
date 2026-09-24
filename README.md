# HRM Pro — Human Resource Management System

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

**EN:** A web-based HR management system covering employees, time attendance, leave, payroll, performance, and training. Built with FastAPI and SQLAlchemy.

**TH:** ระบบบริหารงานบุคคลบนเว็บ ครอบคลุมข้อมูลพนักงาน เวลาเข้างาน การลา เงินเดือน การประเมินผล และการฝึกอบรม พัฒนาด้วย FastAPI และ SQLAlchemy

> **Status:** Working prototype / portfolio project. Not yet production-hardened.
> สถานะ: ต้นแบบที่ใช้งานได้ (prototype) ยังไม่พร้อมใช้งานจริงระดับ production

---

## Screenshots

<!-- Upload images to docs/screenshots/ then remove this comment -->
| Dashboard | Employees | Payslip |
|---|---|---|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Employees](docs/screenshots/employees.png) | ![Payslip](docs/screenshots/payslip.png) |

---

## Features & Status

✅ Implemented · 🟡 Partial · 📝 Planned

| Module | Feature | Status |
|---|---|---|
| **Employee Management** | Profile, contract, salary history, document attachments | ✅ |
| | Org chart, position change history | ✅ |
| **Time Attendance** | Check-in/out, shifts, OT, late/absence calculation | ✅ |
| | Attendance report export (pre-payroll) | ✅ |
| | Mobile / face / fingerprint / GPS check-in | 📝 |
| **Leave Management** | Online leave request, leave types, balance display | ✅ |
| | Multi-level approval workflow | ✅ |
| **Payroll** | Salary calculation with tax, social security, provident fund | ✅ |
| | Online payslip | ✅ |
| | Government form integration, bank file export, printer output | 📝 |
| **Performance** | KPI evaluation, multi-level workflow, dashboard | ✅ |
| **Training** | Training records and planning | ✅ |
| | Certificate expiry alerts | 🟡 |
| **Security** | Role-based access control (RBAC), activity log | ✅ |
| | Data backup | 🟡 |
| | PDPA / GDPR compliance review | 📝 |

---

## Tech Stack

- **Backend:** Python 3.8+, FastAPI
- **ORM / Database:** SQLAlchemy, SQLite
- **Frontend:** Jinja2 templates, Tailwind CSS (standalone), Font Awesome 6
- **Assets:** served locally (offline-capable, no CDN dependency)

---

## Getting Started

```bash
# 1. Clone
git clone https://github.com/monkawee/hrm-pro.git
cd hrm-pro

# 2. Virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create database and seed demo data
python -m app.seed

# 5. Run
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

**Demo login (local seed data only):** `admin` / `1234`

---

## Development Notes

This project was built with AI-assisted development. I defined the requirements, HR business rules, and module scope, then reviewed, tested, and integrated the generated code.

โปรเจกต์นี้พัฒนาโดยใช้ AI ช่วยเขียนโค้ด ผู้พัฒนากำหนด requirement, business rule ด้าน HR และขอบเขตของแต่ละโมดูล จากนั้นตรวจสอบ ทดสอบ และประกอบระบบเอง

---

## License

Copyright © 2024–2026 Monkawee Maneewalaya. **All rights reserved.**
Source code is visible for portfolio and evaluation purposes only. See [LICENSE](LICENSE).
For commercial licensing: generalmaitri@hotmail.com
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

## 🛤️ Implementation Roadmap

- [x] **1. ระบบเวลาเข้างาน (Time Attendance)**
  - ลงเวลา (มือถือ/หน้า/นิ้ว/GPS), รองรับกะ/OT, คำนวณขาดลามาสาย, และ **Export Report ก่อนทำเงินเดือน**
- [x] **2. เงินเดือน (Payroll)**
  - คำนวณอัตโนมัติ, รองรับภาษี/ประกันสังคม/กองทุน (**เชื่อมต่ออัปเดตฟอร์มรัฐบาลได้**), Import OT, **ออก Slip ออนไลน์ (เชื่อมปริ๊นเตอร์ได้)**, Export ไฟล์ธนาคาร
- [x] **3. ระบบลา (Leave Management)**
  - ลาออนไลน์ผ่านมือถือ, ตั้งประเภทลา, Workflow อนุมัติหลายขั้น, แสดงสิทธิคงเหลือ Real-time
- [x] **4. Performance / Evaluation**
  - ประเมิน KPI, Workflow หลายระดับ, Dashboard วิเคราะห์ข้อมูล
- [x] **5. Training / Development**
  - บันทึกประวัติอบรม (รองรับ ISO), วางแผน Training, แจ้งเตือน Certificate หมดอายุ, แบบประเมินผล
- [x] **6. ข้อมูลพนักงาน (Employee Management)**
  - เก็บประวัติครบถ้วน (Profile, สัญญา, เงินเดือน), แนบเอกสารสำคัญ, Org Chart, ประวัติปรับตำแหน่ง
- [x] **7. Security & Compliance**
  - กำหนดสิทธิ์ผู้ใช้, Log การใช้งาน, Backup ข้อมูล, และ **รองรับ PDPA/GDPR**

Developed with ❤️ by monkawee
