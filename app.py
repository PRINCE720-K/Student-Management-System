from flask import Flask, flash, render_template, request, redirect, send_file, session, url_for
import student_management as sm
import sqlite3
import os
from werkzeug.utils import secure_filename
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, TableStyle,Table,Image
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
import random
from db_config import get_db_path,change_db_path,load_path
from werkzeug.security import generate_password_hash, check_password_hash
import io
import sys

app = Flask(__name__)
app.secret_key = "secret123"

if not load_path():
    change_db_path()
    
def get_upload_folder():
    db_folder = os.path.dirname(get_db_path())
    upload_path = os.path.join(db_folder, "uploads")

    os.makedirs(upload_path, exist_ok=True)
    return upload_path

app.config["UPLOAD_FOLDER"] = get_upload_folder()

# ================= AUTO DB INIT =================

@app.before_request
def auto_db():
    sm.init_db()

# ================= USER CHECK =================
def is_user_exist():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    user = cur.fetchone()

    conn.close()
    return True if user else False
# ----------------- CHANGE DB PATH ----------------
@app.route("/change_db_path")
def change_path():
    if "user" not in session:
        return redirect("/login")

    if change_db_path():
            sm.init_db()
            flash("✅ Database Path Updated!", "success")
    else:
            flash("❌ Path not changed Restart the Application ", "error")

    return redirect("/login")

# ================= SHOW DB PATH =================
@app.route("/show_db_path")
def show_db_path():
    if "user" not in session:
        return redirect("/login")

    path = get_db_path()
    flash(f"📁 Current DB Path: {path}", "info")
    return redirect("/dashboard")

# ================= ADD USER (ADMIN ONLY) =================

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if session.get("role") != "admin":
        return "Access Denied"

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        hashed_password = generate_password_hash(password)

        try:
            with sqlite3.connect(get_db_path()) as conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO users(username, password, role)
                    VALUES (?, ?, ?)
                """, (username, hashed_password, role))
                conn.commit()

            flash("User created successfully", "success")

        except:
            flash("Username already exists", "error")

    return render_template("add_user.html")

# --------------- Delete USER (ADMIN ONLY) ---------------
@app.route("/delete_user/<int:id>")
def delete_user(id):

    if session.get("role") != "admin":
        return "Access Denied"

    try:
        with sqlite3.connect(get_db_path()) as conn:
            cur = conn.cursor()

            # ❌ prevent deleting self (optional but recommended)
            cur.execute("SELECT username FROM users WHERE id=?", (id,))
            user = cur.fetchone()

            if user and user[0] == session.get("user"):
                flash("You cannot delete yourself", "warning")
                return redirect("/manage_users")

            cur.execute("DELETE FROM users WHERE id=?", (id,))
            conn.commit()

        flash("User deleted successfully", "success")

    except:
        flash("Error deleting user", "error")

    return redirect("/manage_users")

# ------------------ Change User Password (ADMIN ONLY)---------------------

@app.route("/change_password_user/<int:id>", methods=["GET","POST"])
def change_password_user(id):

    if session.get("role") != "admin":
        return "Access Denied"

    if request.method == "POST":
        new_pass = request.form["new_password"]

        from werkzeug.security import generate_password_hash
        hashed = generate_password_hash(new_pass)

        with sqlite3.connect(get_db_path()) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE users SET password=? WHERE id=?", (hashed, id))
            conn.commit()

        flash("Password updated", "success")
        return redirect("/manage_users")

    return render_template("change_password_user.html", user_id=id)

# -----------Manage User (ADMIN ONLY)---------------
@app.route("/manage_users")
def manage_users():

    if session.get("role") != "admin":
        return "Access Denied"

    with sqlite3.connect(get_db_path()) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, role FROM users")
        users = cur.fetchall()

    return render_template("manage_users.html", users=users)

# ================= REGISTER =================
@app.route("/register", methods=["GET","POST"])
def register():

    if is_user_exist():
        return redirect("/login")

    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        # 🔐 HASH PASSWORD
        hashed_password = generate_password_hash(p)

        conn = sqlite3.connect(get_db_path())
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users(username, password, role)
            VALUES (?, ?, ?)
        """, (u, hashed_password, "admin"))

        conn.commit()
        conn.close()

        flash("Admin created successfully", "success")
        return redirect("/login")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():

    if not is_user_exist():
        return redirect("/register")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect(get_db_path()) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, password, role FROM users WHERE username=?", (username,))
            user = cur.fetchone()

        if user and check_password_hash(user[1], password):
            session["user"] = username
            session["role"] = user[2]

            flash("Login successful", "success")
            return redirect("/dashboard")

        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- PROTECT FUNCTION ----------------
def login_required():
    if "user" not in session:
        return False
    return True

# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot_password", methods=["GET","POST"])
def forgot_password():
    if request.method == "POST":
        u = request.form["username"]
        role = request.form["role"]
        new = request.form["new_password"]

        hashed = generate_password_hash(new)

        conn = sqlite3.connect(get_db_path())
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND role=?", (u, role))
        user = cur.fetchone()

        if user:
            cur.execute("UPDATE users SET password=? WHERE username=? AND role=?",
                        (hashed, u, role))
            conn.commit()
            conn.close()
            return render_template("forgot_password.html", msg="✅ Password Reset Success")
        else:
            conn.close()
            return render_template("forgot_password.html", msg="❌ User Not Found")

    return render_template("forgot_password.html")


# ---------------- HOME ----------------
@app.route("/")
def home():
    if not login_required():
        return redirect("/login")
    return render_template("dashboard.html")

# ---------------- STUDENTS ----------------
@app.route("/students")
def students():
    if not login_required():
        return redirect("/login")

    selected_class = request.args.get("class")

    data = sm.get_students()
    return render_template("students.html", students=data, selected_class=selected_class)

# ---------------- ADD STUDENT ----------------
@app.route("/add", methods=["GET","POST"])
def add():
    if not login_required():
        return redirect("/login")

    # admin only
    if session.get("role") != "admin":
        flash("❌ Access Denied", "error")
        return redirect("/students")

    if request.method == "POST":
        roll = request.form["roll"]
        name = request.form["name"].upper()
        cls = request.form["class"].upper()
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        father_name = request.form["father_name"].upper()
        mother_name = request.form["mother_name"].upper()
        birth_date = request.form["birth_date"]
        gender = request.form["gender"]
        addmission_date = request.form["admission_date"]

        file = request.files.get("photo")
        filename = None

        # file upload safe
        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        if sm.insert_student_data(roll,name,father_name,mother_name,birth_date,gender,cls,email,phone,address,filename,addmission_date):
            flash("✅ Admission Successful ", "success")
        else:
            flash("❌ Admission Failed! Possible Duplicate Roll No.", "error")
        return redirect("/students")

    return render_template("add_student.html")

# ---------------- UPDATE_FULL_VIEW ----------------
@app.route("/update_full", methods=["POST"])
def update_full():
    if session.get("role") != "admin":
        flash("❌ Access Denied", "error")
        return redirect("/students") 

    roll = request.form["roll"]
    cls = request.form["class"]
    name = request.form["name"]
    phone = request.form["phone"]
    email = request.form["email"]
    address = request.form["address"]

    file = request.files["photo"]
    filename = None

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    if filename:
        sm.update_student_data(roll, cls, name, phone, email, address, filename)
    else:
        sm.update_student_data(roll, cls, name, phone, email, address, None)

    flash("✅ Student Data Updated!", "success")

    return redirect("/students")

# ---------------- DELETE ----------------
@app.route("/delete/<int:roll>/<string:cls>/<photo>")
def delete(roll, cls, photo):
    if not login_required():
        return redirect("/login")

    if session.get("role") != "admin":
        flash("❌ Access Denied", "error")
        return redirect("/students")


    if sm.delete_student_data(roll, cls, photo):
        flash("✅ Student Data Deleted", "success")
    else:
        flash("❌ Deletion Failed!", "error")
    return redirect("/students")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    with sqlite3.connect(get_db_path()) as conn:
        cur = conn.cursor()

        # 🔢 TOTAL
        cur.execute("SELECT COUNT(*) FROM students")
        total = cur.fetchone()[0] or 0

        # 📊 STATUS
        cur.execute("SELECT COUNT(*) FROM students WHERE status='ACTIVE'")
        active = cur.fetchone()[0] or 0

        cur.execute("SELECT COUNT(*) FROM students WHERE status='PASSED'")
        passed = cur.fetchone()[0] or 0

        cur.execute("SELECT COUNT(*) FROM students WHERE status='LEFT'")
        left = cur.fetchone()[0] or 0

        # 📉 PASS / FAIL
        cur.execute("""
        SELECT 
        SUM(CASE WHEN (marks*100.0/max_marks) >= 40 THEN 1 ELSE 0 END),
        SUM(CASE WHEN (marks*100.0/max_marks) < 40 THEN 1 ELSE 0 END)
        FROM marks
        """)
        pf = cur.fetchone()
        pass_count = pf[0] or 0
        fail_count = pf[1] or 0

        # 📅 AVG ATTENDANCE
        cur.execute("SELECT AVG(attendance) FROM attendance")
        avg_att = cur.fetchone()[0] or 0

            # 📈 MONTHLY ATTENDANCE
        cur.execute("""
        SELECT month, AVG(attendance)
        FROM attendance
        GROUP BY month
        ORDER BY month
        """)
        att_data = cur.fetchall()

        months = [r[0] for r in att_data] if att_data else []
        att_values = [round(r[1], 2) for r in att_data] if att_data else []

        # 📊 CLASS PERFORMANCE
        cur.execute("""
        SELECT class,
        AVG((marks*100.0)/max_marks)
        FROM students s
        JOIN marks m ON s.id = m.student_id
        GROUP BY class
        """)
        class_data = cur.fetchall()

        classes = [c[0] for c in class_data] if class_data else []
        class_perf = [round(c[1], 2) for c in class_data] if class_data else []

        # 🏆 TOPPER
        cur.execute("""
        SELECT s.name, s.class,
        SUM(marks)*100.0/SUM(max_marks)
        FROM students s
        JOIN marks m ON s.id = m.student_id
        GROUP BY s.id
        ORDER BY 3 DESC
        LIMIT 1
        """)
        topper = cur.fetchone()

    return render_template(
        "dashboard.html",
        total=total,
        active=active,
        passed=passed,
        left=left,
        pass_count=pass_count,
        fail_count=fail_count,
        avg_att=round(avg_att, 2),
        months=months,
        att_values=att_values,
        classes=classes,
        class_perf=class_perf,
        topper=topper
    )

# ---------------- SUBJECTS ----------------
@app.route("/subjects", methods=["GET","POST"])
def subjects():
    
    if session.get("role") != "admin":
        flash("❌ Access Denied", "error")
        return redirect("/students")
    
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    if request.method == "POST":
        sub = request.form["subject"].upper()
        try:
            if sm.subject_menu(sub):
                flash("✅ Subject Added!", "success")
            else:
                flash("❌ Subject already exists!", "error")
        except:
            pass

    cur.execute("SELECT * FROM subjects")
    data = cur.fetchall()

    conn.close()
    return render_template("subjects.html", subjects=data)

# ---------------- DELEATE SUBJECT --------------
@app.route("/delete_subject/<int:id>")
def delete_subject(id):

    if session.get("role") != "admin":
        flash("❌ Access Denied", "error")
        return redirect("/students")
    
    if sm.delete_subject:
        flash("Subject deleted", "warning")
    return redirect("/subjects")

# ------------ UPDATE SUBJECT ------------------
@app.route("/update_subject", methods=["POST"])
def update_subject():
    if session.get("role") != "admin":
        flash("❌ Access Denied", "error")
        return redirect("/students")
    
    id = request.form["id"]
    name = request.form["subject"]

    if sm.update_subject(id,name):
        flash("Subject updated", "success")
    
    return redirect("/subjects")


# ---------------- ADD MARKS ----------------
@app.route("/add_marks", methods=["GET","POST"])
def add_marks():
    with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

    if request.method == "POST":
        roll = request.form["roll"]
        cls = request.form["class"].upper()
        subject = request.form["subject"]
        marks = request.form["marks"]
        max_marks = request.form["max_marks"]

        # validation
        if not roll or not cls or not subject or not marks or not max_marks:
            flash("❌ All fields are required!", "error")
            return redirect("/add_marks")

        # get student
        cur.execute("SELECT id FROM students WHERE roll_no=? AND class=?", (roll, cls))
        student = cur.fetchone()

        if not student:
            flash("❌ Student not found!", "error")
            return redirect("/add_marks")

        # get subject
        cur.execute("SELECT subject_id FROM subjects WHERE subject_name=?", (subject,))
        sub = cur.fetchone()

        if not sub:
            flash("❌ Subject not found!", "error")
            return redirect("/add_marks")

        if sm.insert_student_marks(student[0], sub[0], marks, max_marks):
            flash("✅ Marks added successfully!", "success")
        else:
             flash("❌ Duplicate entry! Marks already exist for this subject.", "error")
           

        return redirect("/add_marks")
    #load class
    cur.execute("SELECT DISTINCT class FROM students WHERE STATUS='ACTIVE'")
    classes = cur.fetchall()

    # load subjects
    cur.execute("SELECT * FROM subjects ")
    subjects = cur.fetchall()

    return render_template("add_marks.html", classes=classes, subjects=subjects)
# ---------------- VIEW MARKS ----------------
@app.route("/marks")
def marks():
    cls = request.args.get("class")
    search = request.args.get("search")

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()


    query = """
    SELECT m.id, s.roll_no, s.name, s.class,
           sub.subject_name, m.marks,m.max_marks
    FROM marks m
    JOIN students s ON m.student_id = s.id 
    JOIN subjects sub ON m.subject_id = sub.subject_id
    WHERE 1=1
    """

    params = []

    if cls:
        query += " AND s.class=?"
        params.append(cls.upper())

    if search:
        query += " AND s.roll_no LIKE ?"
        params.append("%"+search+"%")

    cur.execute(query, params)
    data = cur.fetchall()

    conn.close()

    return render_template("marks.html", marks=data)

# ---------------- UPDATE MARKS ----------------
@app.route("/update_marks/<int:id>", methods=["GET","POST"])
def update_marks(id):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    if request.method == "POST":
        new_marks = request.form["marks"]
        new_max_marks = request.form["max_marks"]

        if sm.update_student_marks(id, new_marks, new_max_marks):
            flash("✅ Marks Updated!", "success")
        else:
            flash("❌ Update Failed!", "error")

        return redirect("/marks")

    cur.execute("SELECT * FROM marks WHERE id=?", (id,))
    data = cur.fetchone()

    conn.close()
    return render_template("update_marks.html", data=data)

# ---------------- DELETE MARKS ----------------
@app.route("/delete_marks/<int:id>")
def delete_marks(id):
    if session.get("role") != "admin":
        flash("❌ Access Denied!", "error")
        return redirect("/marks")
    

    if sm.delete_student_marks(id):
        flash("🗑 Marks Deleted", "success")
    else:
        flash("❌ Deletion Failed!", "error")
        
    return redirect("/marks")

# ---------------- ATTENDANCE ----------------
@app.route("/attendance", methods=["GET","POST"])
def attendance():
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    if request.method == "POST":
        roll = request.form["roll"]
        cls = request.form["class"].upper()
        month = request.form["month"].upper()
        att = request.form["attendance"]

        cur.execute("SELECT id FROM students WHERE roll_no=? AND class=?", (roll, cls))
        student = cur.fetchone()

        if not student:
            flash("❌ Student not found", "error")
            return redirect("/attendance")

        student_id = student[0]

        # ❌ DUPLICATE CHECK
        cur.execute("SELECT * FROM attendance WHERE student_id=? AND month=?", (student_id, month))
        if cur.fetchone():
            flash("❌ Attendance already exists for this month!", "error")
            conn.close()
            return redirect("/attendance")

        # ✅ INSERT

        if sm.insert_student_attendance(roll, cls, month, att):
            flash("✅ Attendance Added!", "success")
        else:
            flash("❌ Failed to add attendance!", "error")

        return redirect("/attendance")

    conn.close()
    return render_template("attendance.html")

# ---------------- VIEW ATTENDANCE ----------------
@app.route("/view_attendance")
def view_attendance():
    cls = request.args.get("class")
    roll = request.args.get("roll")

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    query = """
    SELECT s.roll_no, s.name, s.class, a.month, a.attendance, a.id
    FROM attendance a
    JOIN students s ON a.student_id = s.id
    WHERE 1=1
    """

    params = []

    # Class filter
    if cls:
        query += " AND s.class=?"
        params.append(cls.upper())

    # Roll filter
    if roll:
        query += " AND s.roll_no=?"
        params.append(roll)

    cur.execute(query, params)
    data = cur.fetchall()

    conn.close()

    return render_template("view_attendance.html", data=data)

#----------------- DELETE ATTENDANCE ----------------
@app.route("/delete-attendance/<int:id>")
def delete_attendance(id):

    if session.get("role") != "admin":
        flash("❌ Access Denied!", "error")
        return redirect("/view_attendance")
    
    if sm.delete_student_attendance(id):
        flash("🗑 Attendance Deleted", "success")
    else:
        flash("❌ Deletion Failed!", "error")

    return redirect("/view_attendance")

# ---------------- UPDATE ATTENDANCE ----------------
@app.route("/update-attendance/<int:id>", methods=["GET","POST"])
def update_attendance(id):
    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    if request.method == "POST":
        new_att = request.form["attendance"]

        if sm.update_student_attendance(id, new_att):
            flash("✅ Attendance Updated!", "info")
        else:
            flash("❌ Update Failed!", "error")

        return redirect("/view_attendance")

    cur.execute("SELECT * FROM attendance WHERE id=?", (id,))
    data = cur.fetchone()
    conn.close()

    return render_template("update_attendance.html", data=data)

# ---------------- STUDENTS REPORT ------------
@app.route("/student_report")
def student_report():
    roll = request.args.get("roll")
    cls = request.args.get("class")

    if not roll or not cls:
        return render_template("student_report.html", data=None)

    report = sm.get_student_report(get_db_path(), roll, cls)

    if not report:
        return render_template("student_report.html", data=None)

    return render_template(
        "student_report.html",
        data=report["data"],
        total=report["total"],
        percentage=report["percentage"],
        grade=report["grade"],
        result=report["result"],
        attendance_percent=report["attendance"]
    )

# ================ STUDENT INFO =================
@app.route("/student/<string:roll>/<string:cls>")
def student_info(roll, cls):
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE roll_no=? AND class=?", (roll, cls))
    student = cur.fetchone()

    conn.close()

    return render_template("student_info.html", s=student)

# ---------------- PROMOTE CLASS ----------------
@app.route("/promotion_page")
def promotion_page():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE status='ACTIVE'")
    data = cur.fetchall()

    conn.close()

    return render_template("promotion.html", students=data)
# ---------------- AUTO PROMOTE ----------------
@app.route("/auto_promote", methods=["POST"])
def auto_promote():

    cls = request.form.get("class")

    result = sm.promote_students(get_db_path(), cls)

    if result == "success":
        flash("🎓 Promotion Done!", "success")
    elif result == "no_data":
        flash("⚠️ No students!", "warning")
    else:
        flash("❌ Error!", "error")

    return redirect("/promotion_page")


# ---------------- RE-EXAM PROMOTE ----------------
@app.route("/reexam_promote/<int:id>")
def reexam_promote_route(id):
    result = sm.reexam_promote(get_db_path(), id)

    if result == "success":
        flash("🎓 Re-exam PASS → Promoted!", "success")
    elif result == "still_fail":
        flash("❌ Still Failed!", "error")
    else:
        flash("❌ Error!", "error")

    return redirect("/students")


# ---------------- LEAVE STUDENT ----------------
@app.route("/leave_student/<int:id>")
def leave_student(id):
    sm.make_student_leave(get_db_path(), id)

    flash("🚫 Student Marked as LEFT", "warning")
    return redirect("/students")

# ------------------ promotion history ------------------
@app.route("/promotion_history")
def promotion_history():
    data = sm.get_promotion_history(get_db_path())
    return render_template("promotion_history.html", data=data)


# ------------------ history ------------------
@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    year = request.args.get("year")
    cls = request.args.get("class")
    roll = request.args.get("roll")

    conn = sqlite3.connect(get_db_path())
    cur = conn.cursor()

    query = "SELECT * FROM student_history WHERE 1=1"
    params = []

    # 🔥 FILTERS
    if year:
        query += " AND year=?"
        params.append(year)

    if cls:
        query += " AND class=?"
        params.append(cls.upper())

    if roll:
        query += " AND roll_no=?"
        params.append(roll)

    cur.execute(query, params)
    students = cur.fetchall()

    conn.close()

    return render_template(
        "history.html",
        students=students,
        selected_year=year,
        selected_class=cls,
        selected_roll=roll
    )
# ------------------ history report ------------------
@app.route("/history_report")
def history_report():

    roll = request.args.get("roll")
    cls = request.args.get("class")
    year = request.args.get("year")

    if not roll or not cls or not year:
        return render_template("history_report.html", data=None)

    report = sm.get_history_report(get_db_path(), roll, cls, year)

    return render_template("history_report.html", data=report)

@app.route("/history_student_detail")
def history_student_detail():

    roll = request.args.get("roll")
    cls = request.args.get("class")
    year = request.args.get("year")

    if not roll or not cls or not year:
        return render_template("student_info_history.html", data=None)

    data = sm.get_history_student_detail(get_db_path(), roll, cls, year)

    return render_template("student_info_history.html", data=data)

# ------------------PDF-------------------------
@app.route("/download_report/<int:roll>/<cls>")
def download_report(roll, cls):

    data = sm.get_student_report(get_db_path(), roll, cls)

    if not data:
        return "No Data Found"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    # 🎨 CUSTOM STYLES
    title_style = ParagraphStyle(
        'title',
        fontSize=22,
        textColor=colors.darkblue,
        spaceAfter=10
    )

    section_style = ParagraphStyle(
        'section',
        fontSize=12,
        textColor=colors.white,
        backColor=colors.darkblue,
        leftIndent=5,
        spaceAfter=8
    )

    normal = styles["Normal"]

    elements = []
    first = data["data"][0]

    # 🔥 HEADER (LOGO + TITLE + ICON)
    header = []

    logo_path = "static/logo.png"
    cap_path = "static/cap.png"

    logo = Image(logo_path, width=60, height=60) if os.path.exists(logo_path) else ""
    cap = Image(cap_path, width=40, height=40) if os.path.exists(cap_path) else ""

    header.append([logo, Paragraph("<b>STUDENT REPORT</b>", title_style), cap])

    header_table = Table(header, colWidths=[70, 300, 70])
    elements.append(header_table)

    elements.append(Spacer(1, 15))

    # 📷 PHOTO + INFO
    photo_path = f"static/uploads/{first[7]}"

    photo = Image(photo_path, width=80, height=80) if first[7] and os.path.exists(photo_path) else ""

    info = Table([
        ["Student Name:", first[2]],
        ["Roll No:", first[1]],
        ["Class:", first[3]],
        ["Year:", "2025-26"]
    ])

    info.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))

    top_section = Table([
        [info, photo]
    ], colWidths=[350, 100])

    elements.append(top_section)
    elements.append(Spacer(1, 15))

    # 🎨 SUBJECT HEADER BLOCK
    elements.append(Paragraph("SUBJECTS", section_style))

    # 📊 SUBJECT TABLE
    table_data = [["Subject", "Marks", "Grade"]]

    for d in data["data"]:
        percent = (d[5] / d[6]) * 100 if d[6] else 0

        if percent >= 90:
            grade = "A+"
        elif percent >= 75:
            grade = "A"
        elif percent >= 60:
            grade = "B"
        elif percent >= 40:
            grade = "C"
        else:
            grade = "F"

        table_data.append([d[4], f"{d[5]}/{d[6]}", grade])

    table = Table(table_data, colWidths=[200, 100, 80])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke)
    ]))

    elements.append(table)
    elements.append(Spacer(1, 15))

    # 🎨 SUMMARY BLOCK
    elements.append(Paragraph("SUMMARY", section_style))

    result_color = colors.green if data["result"] == "PASS" else colors.red

    summary = Table([
        ["Total Marks", data["total"]],
        ["Percentage", f"{data['percentage']} %"],
        ["Attendance", f"{data['attendance']} %"],
        ["Result", data["result"]],
    ])

    summary.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ('TEXTCOLOR',(0,3),(1,3), result_color)
    ]))

    elements.append(summary)
    elements.append(Spacer(1, 20))

    # 🎓 GRADE SCALE
    elements.append(Paragraph("GRADE SCALE", section_style))

    grade_table = Table([
        ["A+ = 90-100", "B = 60-74", "D = 30-39"],
        ["A = 75-89", "C = 40-59", "F = <30"]
    ])

    grade_table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.5,colors.grey)
    ]))

    elements.append(grade_table)
    elements.append(Spacer(1, 30))

    # ✍ SIGNATURE
    sign = Table([
        ["__________________", "__________________"],
        ["Teacher Signature", "Principal Signature"]
    ])

    sign.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'CENTER')
    ]))

    elements.append(sign)

    # BUILD
    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer,
                     as_attachment=True,
                     download_name="report.pdf",
                     mimetype='application/pdf')

from flask import send_from_directory
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# import sys, os

# def resource_path(path):
#     if getattr(sys, 'frozen', False):
#         return os.path.join(sys._MEIPASS, path)
#     return os.path.join(os.path.abspath("."), path)

# app = Flask(
#     __name__,
#     template_folder=resource_path("templates"),
#     static_folder=resource_path("static")
# )

#---------------- RUN ----------------
if __name__ == "__main__":

    sm.init_db()
    app.run(debug=False, use_reloader=False)


