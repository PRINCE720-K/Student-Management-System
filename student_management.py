from fileinput import filename
import os
from db_config import get_db_path
import sqlite3
from datetime import datetime
# # ---------------- DATABASE SETUP ----------------
# with sqlite3.connect(get_db_path()) as conn:
#     conn.execute("PRAGMA foreign_keys = ON")
#     cur = conn.cursor()

def init_db():
    with sqlite3.connect(get_db_path()) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        #login table create
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
        """)
        #cur.execute("INSERT INTO users(username,password,role) VALUES('admin','1234','admin')")
        #cur.execute("INSERT INTO users (username,password,role) VALUES ('user','123','user')")
        #student table create
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no INTEGER,
            name TEXT, 
            father_name TEXT,
            mother_name TEXT,
            birth_date TEXT,
            gender TEXT, 
            class TEXT,
            email TEXT,
            photo TEXT,        
            phone TEXT,
            address TEXT,
            addmission_date TEXT, 
            status TEXT DEFAULT 'ACTIVE',  
            UNIQUE(roll_no, class,status)
        )
        """)
        #subjects table create
        cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT UNIQUE
        )
        """)
        #marks table create
        cur.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            marks INTEGER,
            max_marks INTEGER,

            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY(subject_id) REFERENCES subjects(subject_id),

            UNIQUE(student_id, subject_id)
        )
        """)
        #attendance table create
        cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            month TEXT,
            attendance INTEGER,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            
            UNIQUE(student_id, month)
        )
        """)
        #history table create
        cur.execute("""
        CREATE TABLE IF NOT EXISTS promotion_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            roll_no INTEGER,
            name TEXT,
            from_class TEXT,
            to_class TEXT,
            date TEXT,
            result TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
            )
        """)

        # STUDENT HISTORY
        cur.execute("""
        CREATE TABLE IF NOT EXISTS student_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            roll_no INTEGER,
            name TEXT,
            class TEXT,
            year TEXT,
            father_name TEXT,
            mother_name TEXT,
            phone TEXT,
            address TEXT,
            photo TEXT
        )"""
        )

        #  MARKS HISTORY
        cur.execute("""
        CREATE TABLE IF NOT EXISTS marks_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject_id INTEGER,
            marks INTEGER,
            max_marks INTEGER,
            class TEXT,
            year TEXT,
            UNIQUE(student_id, subject_id, year)
        )"""
        )            

        #  ATTENDANCE HISTORY
        cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            month TEXT,
            attendance INTEGER,
            class TEXT,
            year TEXT,
            UNIQUE(student_id, month, year)
        )"""
        )


        conn.commit()



# ---------------- STUDENT ----------------

def insert_student_data(roll,name,father_name,mother_name,birth_date,gender,cls,email,phone,address,photo,addmission_date):
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

            try:
                cur.execute("""
            INSERT INTO students(roll_no,name,father_name,mother_name,birth_date,gender,class,email,phone,address,photo,addmission_date)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
            """, (roll,name,father_name,mother_name,birth_date,gender,cls,email,phone,address,photo,addmission_date))

                conn.commit()
                return True
            except:
                return False

        
def view_student_data():
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()
            for row in conn.execute("SELECT roll_no,name,class FROM students"):
                print(row)

def delete_student_data(roll, cls, photo):
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

            try:
                 if os.path.exists("static/uploads/{photo}".format(photo=photo)):
                    os.remove("static/uploads/{photo}".format(photo=photo))
                 cur.execute("DELETE FROM students WHERE roll_no=? AND class=?", (roll, cls))

                 conn.commit()
                 return True
            
            except:
                 return False

def update_student_data(roll, cls, name, phone, email, address, photo):
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

            cur.execute("""
        UPDATE students
        SET name=?, phone=?, email=?, address=?, photo=?
        WHERE roll_no=? AND class=?
        """, (name, phone, email, address, photo, roll, cls))

            conn.commit()
            return True
        
#get student
def get_students():
    with sqlite3.connect(get_db_path()) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()

        cur.execute("""
    SELECT roll_no, name, class, phone, email, address, photo
    FROM students WHERE status='ACTIVE'
    ORDER BY class, roll_no
    """)

        rows = cur.fetchall()

    grouped = {}

    for row in rows:
        cls = row[2]
        if cls not in grouped:
            grouped[cls] = []
        grouped[cls].append(row)

    return grouped

# ---------------- SUBJECT ----------------
def subject_menu(sub):
    with sqlite3.connect(get_db_path()) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO subjects(subject_name) VALUES(?)",(sub,))
            conn.commit()
            return True
        except:
            return False

def delete_subject(id):
    with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

        
            cur.execute("DELETE FROM subjects WHERE id=?", (id,))
            conn.commit()

            return True

def update_subject(id,name):
    with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

            cur.execute("UPDATE subjects SET name=? WHERE id=?", (name, id))
            conn.commit()
            return True
    
            
# ---------------- MARKS ----------------
def insert_student_marks(student, sub, marks, max_marks):
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

            try:
                cur.execute("""
            INSERT INTO marks(student_id, subject_id, marks, max_marks)
            VALUES (?, ?, ?, ?)
            """, (student, sub, marks, max_marks))
                conn.commit()
                return True
            except:
                return False

def update_student_marks(id, new_marks, new_max_marks):
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

            try:
                cur.execute("UPDATE marks SET marks=?, max_marks=? WHERE id=?", (new_marks, new_max_marks, id))
                conn.commit()
                return True
            except:
                return False


def delete_student_marks(id):
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM marks WHERE id=?", (id,))
                conn.commit()
                return True
            except:
                return False
            
# ---------------- ATTENDANCE ----------------
def insert_student_attendance(roll, cls, month, attendance):
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

            cur.execute("SELECT id FROM students WHERE roll_no=? AND class=?", (roll, cls))
            student = cur.fetchone()

            if not student:
                return False
            
            cur.execute("""
        INSERT INTO attendance(student_id, month, attendance)
        VALUES (?, ?, ?)
        """, (student[0], month, attendance))
            conn.commit()
            return True
        

def update_student_attendance(new_attendance, id):
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()

            try:
                cur.execute("UPDATE attendance SET attendance=? WHERE id=?", (new_attendance, id))
                conn.commit()
                return True
            except:
                return False

def delete_student_attendance(id):
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cur = conn.cursor()
            try:
                cur.execute("DELETE FROM attendance WHERE id=?", (id,))
                conn.commit()
                return True
            except:
                return False

# ---------------- STUDENT REPORT ----------------
def get_student_report(db_path, roll, cls):

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cls = cls.upper()

    # 🔹 Student + Marks
    cur.execute("""
    SELECT s.id, s.roll_no, s.name, s.class,
           sub.subject_name, m.marks, m.max_marks, s.photo
    FROM students s
    LEFT JOIN marks m ON s.id = m.student_id
    LEFT JOIN subjects sub ON m.subject_id = sub.subject_id
    WHERE s.roll_no=? AND s.class=?
    """, (roll, cls))

    data = cur.fetchall()

    # ❌ Student not found
    if not data or data[0][0] is None:
        conn.close()
        return None

    # 🔥 FILTER VALID SUBJECT
    valid_marks = [d for d in data if d[4] is not None]

    total_obtained = sum([d[5] or 0 for d in valid_marks])
    total_max = sum([d[6] or 0 for d in valid_marks])

    percentage = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0

    # 🎯 RESULT + GRADE
    if percentage >= 90:
        grade = "A+"
        result = "PASS"
    elif percentage >= 75:
        grade = "A"
        result = "PASS"
    elif percentage >= 60:
        grade = "B"
        result = "PASS"
    elif percentage >= 40:
        grade = "C"
        result = "PASS"
    else:
        grade = "FAIL"
        result = "FAIL"

    # 🔥 ATTENDANCE
    student_id = data[0][0]

    cur.execute("""
    SELECT AVG(attendance) FROM attendance
    WHERE student_id=?
    """, (student_id,))

    att = cur.fetchone()[0]
    attendance_percent = round(att, 2) if att else 0

    conn.close()

    return {
        "data": valid_marks,
        "total": total_obtained,
        "percentage": percentage,
        "grade": grade,
        "result": result,
        "attendance": attendance_percent
    }

# ---------------- PROMOTION (AUTO RESULT BASED) ----------------
def promote_students(db_path, old_class):

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        try:
            cur.execute("""
            SELECT id FROM students
            WHERE class=? AND status='ACTIVE'
            """, (old_class,))

            students = cur.fetchall()

            if not students:
                return "no_data"

            for (student_id,) in students:

                # 🔥 STEP 1: SAVE HISTORY FIRST
                save_student_history(conn, student_id)

                # 🔹 CALCULATE MARKS
                cur.execute("""
                SELECT SUM(marks), SUM(max_marks)
                FROM marks WHERE student_id=?
                """, (student_id,))

                total, max_total = cur.fetchone()
                total = total or 0
                max_total = max_total or 0

                percentage = (total / max_total * 100) if max_total > 0 else 0
                result = "PASS" if percentage >= 40 else "FAIL"

                # 🔹 PROMOTION LOGIC
                if old_class == "FYCS":
                    new_class = "SYCS" if result == "PASS" else "FYCS"

                elif old_class == "SYCS":
                    new_class = "TYCS" if result == "PASS" else "SYCS"

                elif old_class == "TYCS":
                    if result == "PASS":
                        cur.execute("UPDATE students SET status='PASSED' WHERE id=?", (student_id,))
                        new_class = "PASSED"
                    else:
                        new_class = "TYCS"

                # 🔹 UPDATE CLASS
                if result == "PASS" and new_class != "PASSED":
                    cur.execute("UPDATE students SET class=? WHERE id=?", (new_class, student_id))

                # 🔹 SAVE PROMOTION HISTORY (WITH NAME + ROLL)
                cur.execute("""
                SELECT roll_no, name FROM students WHERE id=?
                """, (student_id,))
                roll, name = cur.fetchone()

                cur.execute("""
                INSERT INTO promotion_history
                (student_id, roll_no, name, from_class, to_class, date, result)
                VALUES (?,?,?,?,?,?,?)
                """, (
                    student_id,
                    roll,
                    name,
                    old_class,
                    new_class,
                    datetime.now().strftime("%Y-%m-%d"),
                    result
                ))

                # 🔥 CLEAR CURRENT DATA
                cur.execute("DELETE FROM marks WHERE student_id=?", (student_id,))
                cur.execute("DELETE FROM attendance WHERE student_id=?", (student_id,))

            conn.commit()
            return "success"

        except Exception as e:
            print("❌ PROMOTION ERROR:", e)
            return "error"
        
# helper to get next roll number in case of collision
def next_roll(cur, cls):
    cur.execute("SELECT COALESCE(MAX(roll_no), 0) FROM students WHERE class=?", (cls,))
    return (cur.fetchone()[0] or 0) + 1

# ---------------- RE-EXAM PROMOTION ----------------
def reexam_promote(db_path, student_id):

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        try:
            # 🔹 STUDENT DATA
            cur.execute("""
            SELECT roll_no, name, class FROM students
            WHERE id=?
            """, (student_id,))
            
            student = cur.fetchone()

            if not student:
                return "not_found"

            # ✅ SAFE ASSIGN
            roll = student[0]
            name = student[1]
            old_class = student[2]

            # 🔹 MARKS CALCULATION
            cur.execute("""
            SELECT marks, max_marks FROM marks
            WHERE student_id=?
            """, (student_id,))
            
            marks_data = cur.fetchall()

            total = sum(m[0] or 0 for m in marks_data)
            max_total = sum(m[1] or 0 for m in marks_data)

            percentage = (total / max_total * 100) if max_total > 0 else 0

            # ❌ STILL FAIL
            if percentage < 40:
                return "still_fail"

            # 🎓 PROMOTION LOGIC
            if old_class == "FYCS":
                new_class = "SYCS"
            elif old_class == "SYCS":
                new_class = "TYCS"
            elif old_class == "TYCS":
                cur.execute("UPDATE students SET status='PASSED' WHERE id=?", (student_id,))
                new_class = "PASSED"
            else:
                return "invalid"

            save_student_history(conn, student_id)

            # 🔄 UPDATE CLASS
            if new_class != "PASSED":
                cur.execute("""
                UPDATE students 
                SET class=?, status='ACTIVE'
                WHERE id=?
                """, (new_class, student_id))
                        # 🔥 UPDATE MARKS HISTORY
            year = datetime.now().strftime("%Y")

            # 🔥 UPDATE OLD HISTORY (FAIL → PASS)
            cur.execute("""
            UPDATE promotion_history
            SET result='PASS'
            WHERE student_id=? AND from_class=? AND result='FAIL' AND date LIKE ?
            """, (student_id, old_class, f"{year}%"))



            cur.execute("""
            UPDATE marks_history
            SET marks = (
                SELECT m.marks FROM marks m
                WHERE m.student_id = marks_history.student_id
                AND m.subject_id = marks_history.subject_id
            )
            WHERE student_id=? AND year=?
            """, (student_id, year))


            # 📜 INSERT NEW PROMOTION HISTORY (FINAL ENTRY)
            cur.execute("""
            INSERT INTO promotion_history
            (student_id, roll_no, name, from_class, to_class, date, result)
            VALUES (?,?,?,?,?,?,?)
            """, (
                student_id,
                roll,
                name,
                old_class,
                new_class,
                datetime.now().strftime("%Y-%m-%d"),
                "PASS"
            ))

            # 🔥 CLEAR CURRENT MARKS & ATTENDANCE             
            cur.execute("DELETE FROM marks WHERE student_id=?", (student_id,))
            cur.execute("DELETE FROM attendance WHERE student_id=?", (student_id,))


            conn.commit()
            return "success"

        except Exception as e:
            print("❌ REEXAM ERROR:", e)
            return "error"

# ---------------- LEAVE STUDENT ----------------
def make_student_leave(db_path, student_id):
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()

        try:
            cur.execute("""
            UPDATE students
            SET status='LEFT'
            WHERE id=?
            """, (student_id,))

            conn.commit()
            return "success"

        except Exception as e:
            print("❌ LEAVE ERROR:", e)
            return "error"
                
# ----------------- GET PROMOTION HISTORY ----------------
def get_promotion_history(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT * FROM promotion_history ORDER BY id DESC")
    data = cur.fetchall()

    conn.close()
    return data

# ----------------- GET YEAR WISE HISTORY ----------------
def get_history_report(db_path, roll, cls, year):

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM student_history
    WHERE roll_no=? AND class=? AND year=?
    ORDER BY id DESC LIMIT 1
    """, (roll, cls, year))

    student = cur.fetchone()

    if not student:
        conn.close()
        return None

    student_id = student[1]

    # 🔹 MARKS
    cur.execute("""
SELECT sub.subject_name, m.marks, m.max_marks
FROM marks_history m
JOIN subjects sub ON m.subject_id = sub.subject_id
WHERE m.student_id=? AND m.class=? AND m.year=?
""", (student_id, cls, year))

    marks = cur.fetchall()

    total = sum(m[1] or 0 for m in marks)
    max_total = sum(m[2] or 0 for m in marks)

    percentage = (total / max_total * 100) if max_total > 0 else 0

    # 🔥 RESULT FROM PROMOTION HISTORY
    cur.execute("""
    SELECT result FROM promotion_history
    WHERE student_id=? AND from_class=?
    ORDER BY id DESC LIMIT 1
    """, (student_id, cls))

    res = cur.fetchone()
    result = res[0] if res else "FAIL"

    conn.close()

    return {
        "student": student,
        "marks": marks,
        "total": total,
        "percentage": round(percentage,2),
        "result": result,
        "year": year
    }

# HELPER TO GET STUDENT CLASS
def get_student_class(conn, student_id):
    cur = conn.cursor()
    cur.execute("SELECT class FROM students WHERE id=?", (student_id,))
    return cur.fetchone()[0]

# HELPER TO SAVE STUDENT HISTORY BEFORE PROMOTION
def save_student_history(conn, student_id):
    cur = conn.cursor()
    year = datetime.now().strftime("%Y")

    # 🔹 GET STUDENT
    cur.execute("""
    SELECT roll_no, name, class FROM students WHERE id=?
    """, (student_id,))
    
    student = cur.fetchone()
    if not student:
        return

    roll, name, cls = student

    # 🔹 SAVE STUDENT HISTORY
    cur.execute("""
    INSERT OR IGNORE INTO student_history (student_id, roll_no, name,father_name, mother_name, phone, address, photo, class, year)
    VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (student_id, roll, name, None, None, None, None, None, cls, year))

    # 🔹 SAVE MARKS HISTORY
    cur.execute("""
    INSERT OR REPLACE INTO marks_history
    (student_id, subject_id, marks, max_marks, class, year)
    SELECT student_id, subject_id, marks, max_marks, ?, ?
    FROM marks WHERE student_id=?
    """, (cls, year, student_id))

    # 🔹 SAVE ATTENDANCE HISTORY
    cur.execute("""
    INSERT INTO attendance_history
    (student_id, month, attendance, class, year)
    SELECT student_id, month, attendance, ?, ?
    FROM attendance WHERE student_id=?
    """, (cls, year, student_id))

# ------------------ GET STUDENT HISTORY DETAIL ----------------
def get_history_student_detail(db_path, roll, cls, year):

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM student_history
    WHERE roll_no=? AND class=? AND year=?
    ORDER BY id DESC LIMIT 1
    """, (roll, cls, year))

    student = cur.fetchone()

    if not student:
        conn.close()
        return None

    student_id = student[1]

    # 🔥 CURRENT STUDENT TABLE से full detail लो
    cur.execute("""
    SELECT name, father_name, mother_name, phone, address, photo
    FROM students
    WHERE id=?
    """, (student_id,))

    extra = cur.fetchone()

    conn.close()

    if not extra:
        return None

    return {
        "roll": student[2],
        "name": extra[0],
        "father": extra[1],
        "mother": extra[2],
        "phone": extra[3],
        "address": extra[4],
        "photo": extra[5],
        "class": student[4],
        "year": year
    }