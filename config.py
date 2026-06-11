"""
Configuration Module - Student Grade Management System
Contains all configuration constants and settings
"""

# Application Information
APP_NAME = "Student Grade Management System"
VERSION = "1.0.0"
UNIVERSITY_NAME = "Malaysian Technical University"

# Database Configuration
DATABASE_NAME = "student_grades.db"

# Departments
DEPARTMENTS = [
    "Computer Science",
    "Information Technology",
    "Software Engineering",
    "Data Science",
    "Cybersecurity",
    "Network Engineering",
    "Artificial Intelligence"
]

# Grade Options
GRADE_OPTIONS = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]

# Semester Options
SEMESTER_OPTIONS = ["Semester 1", "Semester 2", "Semester 3", "Summer"]

# Status Options
STATUS_OPTIONS = ["Active", "Inactive", "Graduated", "Suspended"]

# Grade Points Mapping
GRADE_POINTS = {
    'A': 4.0,
    'A-': 3.7,
    'B+': 3.3,
    'B': 3.0,
    'B-': 2.7,
    'C+': 2.3,
    'C': 2.0,
    'C-': 1.7,
    'D': 1.0,
    'F': 0.0
}

# Default Credentials
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"

# System Performance Thresholds
CPU_WARNING_THRESHOLD = 80
MEMORY_WARNING_THRESHOLD = 80
DISK_WARNING_THRESHOLD = 80

# Color Scheme
PRIMARY_COLOR = "#1e3a8a"
SECONDARY_COLOR = "#3b82f6"
ACCENT_COLOR = "#60a5fa"
SUCCESS_COLOR = "#10b981"
WARNING_COLOR = "#f59e0b"
ERROR_COLOR = "#ef4444"
