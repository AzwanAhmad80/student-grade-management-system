"""
Student Grade Management System - Main Application
Author: [Your Name]
Date: December 2024
Description: A comprehensive student grade management system for universities
"""

import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import psutil
import os

from database import (
    init_db, add_student, get_all_students, update_student, delete_student,
    add_grade, get_student_grades, log_activity, verify_login,
    create_default_user, calculate_gpa
)
from utils import local_css, format_phone_number, validate_email
from config import APP_NAME, VERSION, UNIVERSITY_NAME, DEPARTMENTS, GRADE_OPTIONS, SEMESTER_OPTIONS

# Page Configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Custom CSS
local_css()

# Initialize Database
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = init_db()
    create_default_user()

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ==================== LOGIN PAGE ====================
def login_page():
    """Display login page"""
    st.markdown(f"""
        <div class="main-header">
            <h1>🎓 {APP_NAME}</h1>
            <p>{UNIVERSITY_NAME} - Academic Records Platform</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if verify_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    log_activity(username, "Login", "User logged in")
                    st.success("Login successful!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("Invalid username or password!")
        
        st.info("**Default Credentials:**\n\nUsername: `admin`\n\nPassword: `admin123`")

# ==================== DASHBOARD PAGE ====================
def dashboard_page():
    """Display main dashboard with statistics and charts"""
    st.markdown(f"""
        <div class="main-header">
            <h1>📊 Dashboard</h1>
            <p>Overview of Student Performance & System Statistics</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get statistics
    students_df = get_all_students()
    conn = st.session_state.db_conn
    grades_df = pd.read_sql_query("SELECT * FROM grades", conn)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #3b82f6; margin: 0;">👨‍🎓 Total Students</h3>
                <h1 style="margin: 0.5rem 0;">{len(students_df)}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_students = len(students_df[students_df['status'] == 'Active'])
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #10b981; margin: 0;">✅ Active Students</h3>
                <h1 style="margin: 0.5rem 0;">{active_students}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_courses = grades_df['course_code'].nunique() if not grades_df.empty else 0
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #f59e0b; margin: 0;">📚 Total Courses</h3>
                <h1 style="margin: 0.5rem 0;">{total_courses}</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_score = grades_df['score'].mean() if not grades_df.empty else 0
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #8b5cf6; margin: 0;">📈 Average Score</h3>
                <h1 style="margin: 0.5rem 0;">{avg_score:.2f}%</h1>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Students by Department")
        if not students_df.empty:
            dept_counts = students_df['department'].value_counts()
            fig = px.pie(
    values=dept_counts.values,
    names=dept_counts.index,
    color_discrete_sequence=[
        "#1e3a8a",
        "#2563eb",
        "#3b82f6",
        "#60a5fa",
        "#93c5fd",
        "#bfdbfe",
        "#dbeafe",
        "#1d4ed8",
        "#0ea5e9"
    ]
)
            fig.update_layout(height=400)
            fig.update_layout(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font_color="#1f2937"
)
            fig.update_layout(
    height=400,
    paper_bgcolor="white",
    plot_bgcolor="white",
    font_color="#1f2937",
    showlegend=False
)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No student data available")
    
    with col2:
        st.markdown("### 📈 Grade Distribution")

        if not grades_df.empty:

            grade_counts = grades_df['grade'].value_counts().sort_index()

            fig = px.bar(
                x=grade_counts.index,
                y=grade_counts.values,
                labels={
                    'x': 'Grade',
                    'y': 'Count'
                }
            )

            fig.update_traces(
                marker_color="#2563eb"
            )

            fig.update_layout(
                height=400,
                showlegend=False,
                paper_bgcolor="white",
                plot_bgcolor="white",
                font_color="#1f2937"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.info("No grade data available")
    
    # Recent Students
    st.markdown("### 👥 Recently Enrolled Students")
    if not students_df.empty:
        recent_students = students_df.head(5)[['student_id', 'first_name', 'last_name', 'department', 'enrollment_date', 'status']]
        st.dataframe(recent_students, use_container_width=True, hide_index=True)
    else:
        st.info("No students enrolled yet")

# ==================== ADD STUDENT PAGE ====================
def add_student_page():
    """Display add student form"""
    st.markdown("""
        <div class="main-header">
            <h1>➕ Add New Student</h1>
            <p>Enroll a new student in the system</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        student_id = st.text_input("Student ID *", placeholder="e.g., STU2024001")
        first_name = st.text_input("First Name *", placeholder="Enter first name")
        last_name = st.text_input("Last Name *", placeholder="Enter last name")
        email = st.text_input("Email *", placeholder="student@university.edu.my")
    
    with col2:
        phone = st.text_input("Phone Number", placeholder="+60-12-345-6789")
        department = st.selectbox("Department *", DEPARTMENTS)
        enrollment_date = st.date_input("Enrollment Date")
        status = st.selectbox("Status", ["Active", "Inactive", "Graduated", "Suspended"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("✅ Add Student"):
            if student_id and first_name and last_name and email:
                if not validate_email(email):
                    st.error("Please enter a valid email address!")
                else:
                    student_data = (student_id, first_name, last_name, email, phone, 
                                  department, enrollment_date.strftime("%Y-%m-%d"), status)
                    success, message = add_student(student_data)
                    if success:
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.error("Please fill in all required fields (*)")
    
    with col2:
        if st.button("🔄 Clear Form"):
            st.rerun()

# ==================== MANAGE STUDENTS PAGE ====================
def manage_students_page():
    """Manage Students Page"""

    st.markdown("""
        <div class="main-header">
            <h1>👥 Manage Students</h1>
            <p>Student Management Dashboard</p>
        </div>
    """, unsafe_allow_html=True)

    students_df = get_all_students()

    if students_df.empty:
        st.warning("No students found.")
        return

    # =====================================
    # SUMMARY STATISTICS
    # =====================================

    active_students = len(
        students_df[students_df["status"] == "Active"]
    )

    graduated_students = len(
        students_df[students_df["status"] == "Graduated"]
    )

    total_departments = students_df["department"].nunique()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "👨‍🎓 Total Students",
            len(students_df)
        )

    with col2:
        st.metric(
            "✅ Active Students",
            active_students
        )

    with col3:
        st.metric(
            "🎓 Graduated Students",
            graduated_students
        )

    with col4:
        st.metric(
            "🏢 Departments",
            total_departments
        )

    st.markdown("---")

    # =====================================
    # SEARCH STUDENT
    # =====================================

    search = st.text_input(
        "🔍 Search Student",
        placeholder="Student ID, First Name, Last Name"
    )

    filtered_df = students_df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df["student_id"].astype(str).str.contains(search, case=False) |
            filtered_df["first_name"].astype(str).str.contains(search, case=False) |
            filtered_df["last_name"].astype(str).str.contains(search, case=False)
        ]

    if filtered_df.empty:
        st.warning("No matching student found.")
        return

    # =====================================
    # STUDENT SELECTION
    # =====================================

    selected_student = st.selectbox(
        "Select Student",
        filtered_df["student_id"]
    )

    student = filtered_df[
        filtered_df["student_id"] == selected_student
    ].iloc[0]

    st.markdown("### 🎓 Student Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Student ID:** {student['student_id']}")
        st.write(f"**Name:** {student['first_name']} {student['last_name']}")
        st.write(f"**Email:** {student['email']}")

    with col2:
        st.write(f"**Department:** {student['department']}")
        st.write(f"**Status:** {student['status']}")
        st.write(f"**Phone:** {student['phone']}")

    st.markdown("---")

    # =====================================
    # DELETE STUDENT
    # =====================================

    st.markdown("### 🗑️ Student Actions")

    confirm_delete = st.checkbox(
        "I confirm I want to permanently delete this student"
    )

    if st.button("🗑️ Delete Student"):

        if confirm_delete:

            success, message = delete_student(
                selected_student
            )

            if success:
                st.success(message)
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)

        else:
            st.warning(
                "Please confirm deletion first."
            )

    st.markdown("---")

    # =====================================
    # STUDENT GRADES
    # =====================================

    st.markdown("### 📚 Student Grades")

    grades_df = get_student_grades(
        selected_student
    )

    if grades_df.empty:
        st.info("No grades available.")
        return

    st.dataframe(
        grades_df,
        use_container_width=True,
        hide_index=True
    )

    # =====================================
    # GPA
    # =====================================

    try:
        gpa = calculate_gpa(grades_df)

        st.metric(
            "📈 Current GPA",
            f"{gpa:.2f}"
        )
    except:
        pass

    st.markdown("---")

    # =====================================
    # EDIT STUDENT GRADE
    # =====================================

    st.markdown("### ✏️ Edit Student Grade")

    selected_course = st.selectbox(
        "Select Course",
        grades_df["course_code"]
    )

    grade_row = grades_df[
        grades_df["course_code"] == selected_course
    ].iloc[0]

    grade_options = [
        "A", "A-",
        "B+", "B", "B-",
        "C+", "C", "C-",
        "D", "F"
    ]

    current_grade = grade_row["grade"]

    if current_grade not in grade_options:
        current_grade = "F"

    new_grade = st.selectbox(
        "Grade",
        grade_options,
        index=grade_options.index(current_grade)
    )

    new_score = st.number_input(
        "Score",
        min_value=0.0,
        max_value=100.0,
        value=float(grade_row["score"]),
        step=0.5
    )

    if st.button("💾 Update Grade"):

        try:
            conn = st.session_state.db_conn
            c = conn.cursor()

            c.execute("""
                UPDATE grades
                SET grade=?,
                    score=?
                WHERE student_id=?
                AND course_code=?
            """,
            (
                new_grade,
                new_score,
                selected_student,
                selected_course
            ))

            conn.commit()

            log_activity(
                st.session_state.username,
                "Update Grade",
                f"Updated {selected_student} - {selected_course}"
            )

            st.success(
                "Grade updated successfully!"
            )

            st.rerun()

        except Exception as e:
            st.error(
                f"Update failed: {str(e)}"
            )


# ==================== UPLOAD CSV PAGE ====================
def upload_csv_page():
    """Combined Student + Grade CSV Upload"""

    st.markdown("""
        <div class="main-header">
            <h1>📤 Upload CSV</h1>
            <p>Bulk Import Students and Grades</p>
        </div>
    """, unsafe_allow_html=True)

    st.info(
        "Upload a single CSV containing both student information and grade records."
    )

    st.markdown("### 📥 Download Template")

    template_df = pd.DataFrame({
        "student_id": ["STU2025001"],
        "first_name": ["Ali"],
        "last_name": ["Ahmad"],
        "email": ["ali@email.com"],
        "phone": ["0123456789"],
        "department": ["Information Technology"],
        "enrollment_date": ["2025-01-10"],
        "status": ["Active"],
        "course_name": ["Database Systems"],
        "course_code": ["CS2201"],
        "credits": [3],
        "grade": ["A"],
        "score": [95],
        "semester": ["Semester 1"],
        "academic_year": ["2025"]
    })

    csv_template = template_df.to_csv(index=False)

    st.download_button(
        label="📄 Download Combined Template",
        data=csv_template,
        file_name="student_grade_template.csv",
        mime="text/csv"
    )

    st.markdown("---")

    uploaded_file = st.file_uploader(
        "Choose CSV File",
        type=["csv"]
    )

    if uploaded_file is None:
        return

    try:

        try:
            df = pd.read_csv(
                uploaded_file,
                encoding="utf-8",
                on_bad_lines="skip"
            )
        except:
            uploaded_file.seek(0)

            df = pd.read_csv(
                uploaded_file,
                encoding="latin-1",
                on_bad_lines="skip"
            )

        if df.empty:
            st.error("Uploaded file is empty.")
            return

        df = df.dropna(how="all")

        df.columns = df.columns.str.strip()

        st.markdown("### 👀 Preview Data")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        st.write(
            f"Total Records: {len(df)}"
        )

        required_columns = [
            "student_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "enrollment_date",
            "status",
            "course_name",
            "course_code",
            "credits",
            "grade",
            "score",
            "semester",
            "academic_year"
        ]

        missing_cols = [
            col
            for col in required_columns
            if col not in df.columns
        ]

        if missing_cols:

            st.error(
                f"Missing Columns: {', '.join(missing_cols)}"
            )

            return

        if st.button("✅ Import Data"):

            conn = st.session_state.db_conn

            c = conn.cursor()

            student_inserted = 0
            grade_inserted = 0
            error_count = 0

            errors = []

            progress_bar = st.progress(0)

            status_text = st.empty()

            with st.spinner(
                "Importing data..."
            ):

                for idx, row in df.iterrows():

                    try:

                        progress = (
                            idx + 1
                        ) / len(df)

                        progress_bar.progress(
                            progress
                        )

                        status_text.text(
                            f"Processing row {idx + 1} of {len(df)}"
                        )

                        student_id = str(
                            row["student_id"]
                        ).strip()

                        c.execute(
                            """
                            SELECT student_id
                            FROM students
                            WHERE student_id=?
                            """,
                            (student_id,)
                        )

                        existing_student = c.fetchone()

                        if not existing_student:

                            c.execute(
                                """
                                INSERT INTO students
                                (
                                    student_id,
                                    first_name,
                                    last_name,
                                    email,
                                    phone,
                                    department,
                                    enrollment_date,
                                    status
                                )
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    student_id,
                                    str(row["first_name"]).strip(),
                                    str(row["last_name"]).strip(),
                                    str(row["email"]).strip(),
                                    str(row["phone"]).strip(),
                                    str(row["department"]).strip(),
                                    str(row["enrollment_date"]).strip(),
                                    str(row["status"]).strip()
                                )
                            )

                            student_inserted += 1

                        c.execute(
                            """
                            INSERT INTO grades
                            (
                                student_id,
                                course_name,
                                course_code,
                                credits,
                                grade,
                                score,
                                semester,
                                academic_year
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                student_id,
                                str(row["course_name"]).strip(),
                                str(row["course_code"]).strip(),
                                int(row["credits"]),
                                str(row["grade"]).strip(),
                                float(row["score"]),
                                str(row["semester"]).strip(),
                                str(row["academic_year"]).strip()
                            )
                        )

                        grade_inserted += 1

                    except Exception as e:

                        error_count += 1

                        errors.append(
                            f"Row {idx + 2}: {str(e)}"
                        )

                conn.commit()

            progress_bar.empty()

            status_text.empty()

            st.success(
                f"""
                ✅ Import Completed Successfully

                👨‍🎓 Students Added: {student_inserted}

                📚 Grades Added: {grade_inserted}

                ❌ Errors: {error_count}
                """
            )

            if errors:

                with st.expander(
                    "📋 View Import Errors"
                ):

                    for err in errors[:20]:

                        st.error(err)

            log_activity(
                st.session_state.username,
                "CSV Upload",
                f"Students={student_inserted}, Grades={grade_inserted}, Errors={error_count}"
            )

    except Exception as e:

        st.error(
            f"Upload Failed: {str(e)}"
        )
                
# ==================== SYSTEM PERFORMANCE PAGE ====================
def system_performance_page():
    """Display system performance monitoring page"""
    st.markdown("""
        <div class="main-header">
            <h1>⚡ System Performance</h1>
            <p>Monitor system health and database statistics</p>
        </div>
    """, unsafe_allow_html=True)
    
    # System Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #3b82f6; margin: 0;">💻 CPU Usage</h3>
                <h1 style="margin: 0.5rem 0;">{cpu_usage}%</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #10b981; margin: 0;">🧠 Memory Usage</h3>
                <h1 style="margin: 0.5rem 0;">{memory.percent}%</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #f59e0b; margin: 0;">💾 Disk Usage</h3>
                <h1 style="margin: 0.5rem 0;">{disk.percent}%</h1>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if os.path.exists('student_grades.db'):
            db_size = os.path.getsize('student_grades.db') / (1024 * 1024)
        else:
            db_size = 0
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #8b5cf6; margin: 0;">📊 DB Size</h3>
                <h1 style="margin: 0.5rem 0;">{db_size:.2f} MB</h1>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Performance Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Resource Usage")
        resources = pd.DataFrame({
            'Resource': ['CPU', 'Memory', 'Disk'],
            'Usage': [cpu_usage, memory.percent, disk.percent]
        })
        fig = px.bar(resources, x='Resource', y='Usage', 
                    color='Usage', color_continuous_scale='RdYlGn_r')
        fig.update_layout(height=300, showlegend=False)
        fig.add_hline(y=80, line_dash="dash", line_color="red", 
                     annotation_text="Warning Threshold")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 💿 Memory Details")
        memory_data = pd.DataFrame({
            'Type': ['Used', 'Available'],
            'GB': [memory.used / (1024**3), memory.available / (1024**3)]
        })
        fig = px.pie(memory_data, values='GB', names='Type',
                    color_discrete_sequence=['#3b82f6', '#93c5fd'])
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Database Statistics
    st.markdown("### 📊 Database Statistics")
    
    conn = st.session_state.db_conn
    c = conn.cursor()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        c.execute("SELECT COUNT(*) FROM students")
        student_count = c.fetchone()[0]
        st.metric("Total Students", student_count)
    
    with col2:
        c.execute("SELECT COUNT(*) FROM grades")
        grade_count = c.fetchone()[0]
        st.metric("Total Grades", grade_count)
    
    with col3:
        c.execute("SELECT COUNT(*) FROM activity_log")
        log_count = c.fetchone()[0]
        st.metric("Activity Logs", log_count)
    
    # Recent Activity
    st.markdown("### 📝 Recent Activity Log")
    
    activity_df = pd.read_sql_query(
        "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 20", conn
    )
    
    if not activity_df.empty:
        st.dataframe(activity_df, use_container_width=True, hide_index=True)
    else:
        st.info("No activity logs available")

# ==================== ABOUT PAGE ====================
def about_page():
    """Display about system page"""
    st.markdown("""
        <div class="main-header">
            <h1>ℹ️ About System</h1>
            <p>Student Grade Management System Information</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        ## 🎓 {APP_NAME}
        
        ### Overview
        This comprehensive Student Grade Management System is designed for universities and educational 
        institutions to efficiently manage student records, grades, and academic performance.
        
        ### Key Features
        
        ✅ **Student Management**
        - Add, edit, and delete student records
        - Track student enrollment and status
        - Department-wise organization
        
        ✅ **Grade Management**
        - Record and manage course grades
        - Automatic GPA calculation
        - Semester-wise grade tracking
        
        ✅ **Data Import/Export**
        - Bulk CSV upload for students and grades
        - Individual student data export
        - Template downloads for easy data preparation
        - Robust error handling
        
        ✅ **Analytics & Reporting**
        - Comprehensive dashboard with key metrics
        - Grade distribution analysis
        - Department-wise statistics
        
        ✅ **System Monitoring**
        - Real-time performance monitoring
        - Database statistics
        - Activity logging
        
        ### Technical Stack
        
        - **Frontend:** Streamlit
        - **Database:** SQLite3
        - **Data Processing:** Pandas
        - **Visualizations:** Plotly
        - **System Monitoring:** psutil
        - **Export:** openpyxl
        
        ### Version Information
        - **Version:** {VERSION}
        - **Release Date:** 2024
        - **Last Updated:** December 2024
        """)
    
    with col2:
        st.markdown(f"""
        ### 📞 Contact Information
        
        **{UNIVERSITY_NAME}**  
        Academic Records Department
        
        📧 Email: records@university.edu.my  
        📞 Phone: +60-3-1234-5678  
        🌐 Website: www.university.edu.my
        
        ---
        
        ### 🔒 Security
        
        - Password encryption (SHA-256)
        - Activity logging
        - Secure data storage
        - User authentication
        
        ---
        
        ### 📚 Documentation
        
        For detailed documentation and user guides, please refer to the README.md file or contact the IT department.
        
        ---
        
        ### ⚖️ License
        
        © 2024 {UNIVERSITY_NAME}  
        All rights reserved.
        
        This system is for authorized use only.
        """)
    
    st.markdown("---")
    
    # System Statistics
    st.markdown("### 📊 Current System Statistics")
    
    conn = st.session_state.db_conn
    c = conn.cursor()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        c.execute("SELECT COUNT(*) FROM students")
        st.metric("Total Students", c.fetchone()[0])
    
    with col2:
        c.execute("SELECT COUNT(*) FROM grades")
        st.metric("Total Grades", c.fetchone()[0])
    
    with col3:
        c.execute("SELECT COUNT(DISTINCT department) FROM students")
        st.metric("Departments", c.fetchone()[0])
    
    with col4:
        c.execute("SELECT COUNT(DISTINCT course_code) FROM grades")
        st.metric("Courses", c.fetchone()[0])

# ==================== MAIN APPLICATION ====================
def main():
    """Main application entry point"""

    if not st.session_state.logged_in:
        login_page()
        return

    # Sidebar Navigation
    with st.sidebar:

        st.markdown(
            """
            <div class="sidebar-title">
                🎓 SGMS
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write(f"Welcome, {st.session_state.username}")

        menu = st.radio(
            "Navigation",
            [
                "📊 Dashboard",
                "➕ Add Student",
                "👥 Manage Students",
                "📤 Upload CSV",
                "⚡ System Performance",
                "ℹ️ About",
                "🚪 Logout"
            ]
        )

        st.markdown("---")
        st.write(f"📅 {datetime.now().strftime('%d %B %Y')}")
        st.write(f"🕒 {datetime.now().strftime('%I:%M %p')}")

    # Page Routing
    if menu == "📊 Dashboard":
        dashboard_page()

    elif menu == "➕ Add Student":
        add_student_page()

    elif menu == "👥 Manage Students":
        manage_students_page()

    elif menu == "📤 Upload CSV":
        upload_csv_page()

    elif menu == "⚡ System Performance":
        system_performance_page()

    elif menu == "ℹ️ About":
        about_page()

    elif menu == "🚪 Logout":
        log_activity(
            st.session_state.username,
            "Logout",
            "User logged out"
        )

        st.session_state.logged_in = False
        st.session_state.username = None

        st.success("Logged out successfully!")
        time.sleep(1)
        st.rerun()


if __name__ == "__main__":
    main()
