# 🎓 Student Management System

A complete **Student Management System Desktop Application** built using **Flask + SQLite + PyInstaller**.
This software helps manage students, marks, attendance, reports, and more — all in one place.

---

## 🚀 Features

* 👨‍🎓 Student Management (Add / Update / Delete)
* 📊 Marks Management
* 📅 Attendance Tracking
* 📈 Dashboard with Charts (Chart.js)
* 🏆 Topper Calculation
* 📄 Student Report (PDF Download)
* 🔐 Login System (Admin / User Roles)
* 📁 Upload Student Photos
* 🎯 Promotion System
* 📚 Subject Management
* 📜 History Tracking

---

## 🖥️ Desktop Application

This project is converted into a **.exe desktop software** using:

* PyInstaller
* Inno Setup (for installer)

---

## 📁 Data Storage

All user data is stored locally on the system:

```text
C:\Users\Public\StudentManagementSystem
```

Includes:

* Database (`students.db`)
* Uploaded images (`uploads/`)

⚠️ Data is NOT stored inside the app → safe & portable

---

## 📂 Project Structure

```
student_management/
│
├── app.py
├── main.py
├── db_config.py
├── config.json
│
├── templates/
├── static/
│
├── student_management.py
└── README.md
```

---

## ⚙️ Installation (Developer)

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/student-management-system.git
cd student-management-system
```

---

### 2️⃣ Create virtual environment

```bash
python -m venv env
env\Scripts\activate
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run the app

```bash
python main.py
```

---

## 🛠️ Convert to EXE

```bash
pyinstaller --onefile --windowed ^
--add-data "templates;templates" ^
--add-data "static;static" ^
main.py
```

---

## 📦 Create Installer

Use **Inno Setup** to create `.exe installer`

---

## 🔐 Login System

* First run → Register Admin
* Then login with credentials

---

## 📊 Dashboard Includes

* Total Students
* Active / Passed / Left
* Pass vs Fail Chart
* Monthly Attendance Chart
* Class Performance Chart
* Topper Student

---

## 🧠 Technologies Used

* Python (Flask)
* SQLite
* HTML / CSS / JS
* Chart.js
* PyInstaller
* Inno Setup

---

## ❗ Important Notes

* Do NOT upload:

  * `.db` files
  * `uploads/`
  * `env/`
* Use `.gitignore`

---

## 👨‍💻 Author

**Prince Sandip Kanojiya**

---

## ⭐ Future Improvements

* Cloud Sync ☁️
* Mobile App 📱
* Backup System 💾
* Multi-school Support 🏫

---

## 📜 License

This project is for educational purposes.
