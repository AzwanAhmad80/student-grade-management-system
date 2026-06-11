import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
import streamlit as st
import time

# Database file path
DB_PATH = 'student_grades.db'

def get_connection():
    """Get database connection with timeout"""
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL')  # Write-Ahead Logging for better concurrency
    return conn

def init_db():
    """Initialize database and create tables"""
    conn = get_connection()
    c = conn.cursor()
    
    # Students Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            department TEXT,
            enrollment_date TEXT,
            status TEXT DEFAULT 'Active'
        )
    ''')
    
    # Grades Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            course_name TEXT NOT NULL,
            course_code TEXT NOT NULL,
            credits INTEGER,
            grade TEXT,
            score REAL,
            semester TEXT,
            academic_year TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')
    
    # Users Table (for authentication)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TEXT
        )
    ''')
    
    # Activity Log Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp TEXT,
            details TEXT
        )
    ''')
    
    conn.commit()
    return conn

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_default_user():
    """Create default admin user if not exists"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = st.session_state.db_conn
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username='admin'")
            if not c.fetchone():
                hashed_pw = hash_password("admin123")
                c.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                         ("admin", hashed_pw, "admin", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
            return
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                raise e

def verify_login(username, password):
    """Verify user login credentials"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = st.session_state.db_conn
            c = conn.cursor()
            hashed_pw = hash_password(password)
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_pw))
            result = c.fetchone()
            return result is not None
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                return False

def add_student(student_data):
    """Add a new student to database"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = st.session_state.db_conn
            c = conn.cursor()
            c.execute('''
                INSERT INTO students (student_id, first_name, last_name, email, phone, department, enrollment_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', student_data)
            conn.commit()
            log_activity(st.session_state.username, "Add Student", f"Added student: {student_data[0]}")
            return True, "Student added successfully!"
        except sqlite3.IntegrityError:
            return False, "Student ID or Email already exists!"
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

def get_all_students():
    """Retrieve all students from database"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = st.session_state.db_conn
            df = pd.read_sql_query("SELECT * FROM students ORDER BY enrollment_date DESC", conn)
            return df
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                return pd.DataFrame()

def update_student(student_id, updated_data):
    """Update student information"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = st.session_state.db_conn
            c = conn.cursor()
            c.execute('''
                UPDATE students 
                SET first_name=?, last_name=?, email=?, phone=?, department=?, status=?
                WHERE student_id=?
            ''', (*updated_data, student_id))
            conn.commit()
            log_activity(st.session_state.username, "Update Student", f"Updated student: {student_id}")
            return True, "Student updated successfully!"
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

def delete_student(student_id):
    """Delete student and associated grades"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = st.session_state.db_conn
            c = conn.cursor()
            c.execute("DELETE FROM grades WHERE student_id=?", (student_id,))
            c.execute("DELETE FROM students WHERE student_id=?", (student_id,))
            conn.commit()
            log_activity(st.session_state.username, "Delete Student", f"Deleted student: {student_id}")
            return True, "Student deleted successfully!"
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

def add_grade(grade_data):
    """Add grade record for a student"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = st.session_state.db_conn
            c = conn.cursor()
            c.execute('''
                INSERT INTO grades (student_id, course_name, course_code, credits, grade, score, semester, academic_year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', grade_data)
            conn.commit()
            log_activity(st.session_state.username, "Add Grade", f"Added grade for student: {grade_data[0]}")
            return True, "Grade added successfully!"
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                return False, f"Database error: {str(e)}"
        except Exception as e:
            return False, f"Error: {str(e)}"

def get_student_grades(student_id):
    """Get all grades for a specific student"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = st.session_state.db_conn
            df = pd.read_sql_query("SELECT * FROM grades WHERE student_id=?", conn, params=(student_id,))
            return df
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                return pd.DataFrame()

def calculate_gpa(grades_df):
    """Calculate GPA from grades DataFrame"""
    grade_points = {
        'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 
        'C+': 2.3, 'C': 2.0, 'C-': 1.7, 'D': 1.0, 'F': 0.0
    }
    
    if grades_df.empty:
        return 0.0
    
    total_points = 0
    total_credits = 0
    
    for _, row in grades_df.iterrows():
        if row['grade'] in grade_points:
            total_points += grade_points[row['grade']] * row['credits']
            total_credits += row['credits']
    
    return round(total_points / total_credits, 2) if total_credits > 0 else 0.0

def log_activity(username, action, details):
    """Log user activity with retry mechanism"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = st.session_state.db_conn
            c = conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO activity_log (username, action, timestamp, details) VALUES (?, ?, ?, ?)",
                      (username, action, timestamp, details))
            conn.commit()
            return
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                # Silently fail if activity log fails - don't break the app
                pass

def get_database_stats():
    """Get database statistics"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            conn = st.session_state.db_conn
            c = conn.cursor()
            
            stats = {}
            c.execute("SELECT COUNT(*) FROM students")
            stats['total_students'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM grades")
            stats['total_grades'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(DISTINCT department) FROM students")
            stats['total_departments'] = c.fetchone()[0]
            
            c.execute("SELECT COUNT(DISTINCT course_code) FROM grades")
            stats['total_courses'] = c.fetchone()[0]
            
            return stats
        except sqlite3.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(0.1)
            else:
                return {
                    'total_students': 0,
                    'total_grades': 0,
                    'total_departments': 0,
                    'total_courses': 0
                }
