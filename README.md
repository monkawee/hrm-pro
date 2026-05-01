# 🚀 HRM PRO - Enterprise Employee Management

ระบบบริหารจัดการทรัพยากรบุคคล (HRM) ยุคใหม่ที่เน้นความเร็ว ความปลอดภัย และ UI ที่เป็นมิตรกับผู้ใช้งาน พัฒนาด้วย **FastAPI** และ **SQLAlchemy** พร้อมระบบฐานข้อมูลภายในตัว

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

## ✨ Highlight Features
- 🏢 **Comprehensive HR Modules:** ครอบคลุมการทำงานตั้งแต่ข้อมูลพนักงาน เวลาเข้างาน การลา ไปจนถึงการประเมินผลและฝึกอบรม
- ⚙️ **Automated Payroll & Integration:** ระบบคำนวณเงินเดือนอัตโนมัติที่รองรับทั้งภาษีและประกันสังคม พร้อมการ **เชื่อมต่อระบบฟอร์มรัฐบาล** ได้โดยตรง
- 📱 **Mobile Ready & Paperless:** รองรับการยื่นใบลา และ **ออก Slip เงินเดือนออนไลน์** ผ่านระบบดิจิทัล 100%
- 🔐 **Security & PDPA Compliant:** ปลอดภัยขั้นสุดด้วยระบบแบ่งสิทธิ์ผู้ใช้ (RBAC) เก็บ Log และสอดคล้องกับมาตรฐาน **PDPA/GDPR**
- 🚀 **High Performance & Offline-First:** โหลดทรัพยากร (CSS/Fonts) จากเครื่อง 100% ขับเคลื่อนด้วยความเร็วระดับ Enterprise ของ FastAPI

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

## 🛤️ Implementation Roadmap

- [x] **1. ระบบเวลาเข้างาน (Time Attendance)**
  - ลงเวลา (มือถือ/หน้า/นิ้ว/GPS), รองรับกะ/OT, คำนวณขาดลามาสาย, และ **Export Report ก่อนทำเงินเดือน**
- [x] **2. เงินเดือน (Payroll)**
  - คำนวณอัตโนมัติ, รองรับภาษี/ประกันสังคม/กองทุน (**เชื่อมต่ออัปเดตฟอร์มรัฐบาลได้**), Import OT, **ออก Slip ออนไลน์ (เชื่อมปริ๊นเตอร์ได้)**, Export ไฟล์ธนาคาร
- [x] **3. ระบบลา (Leave Management)**
  - ลาออนไลน์ผ่านมือถือ, ตั้งประเภทลา, Workflow อนุมัติหลายขั้น, แสดงสิทธิคงเหลือ Real-time
- [ ] **4. Performance / Evaluation**
  - ประเมิน KPI, Workflow หลายระดับ, Dashboard วิเคราะห์ข้อมูล
- [ ] **5. Training / Development**
  - บันทึกประวัติอบรม (รองรับ ISO), วางแผน Training, แจ้งเตือน Certificate หมดอายุ, แบบประเมินผล
- [x] **6. ข้อมูลพนักงาน (Employee Management)**
  - เก็บประวัติครบถ้วน (Profile, สัญญา, เงินเดือน), แนบเอกสารสำคัญ, Org Chart, ประวัติปรับตำแหน่ง
- [ ] **7. Security & Compliance**
  - กำหนดสิทธิ์ผู้ใช้, Log การใช้งาน, Backup ข้อมูล, และ **รองรับ PDPA/GDPR**

Developed with ❤️ by monkawee
