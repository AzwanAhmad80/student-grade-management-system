import sqlite3
from datetime import datetime

def create_database():
    """Create database and all required tables"""
    print("Creating database...")
    
    conn = sqlite3.connect('student_grades.db', timeout=10.0)
    
    # Enable WAL mode for better concurrency
    conn.execute('PRAGMA journal_mode=WAL')
    
    c = conn.cursor()
    
    # Students Table
    print("Creating students table...")
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
    print("Creating grades table...")
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
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        )
    ''')
    
    # Users Table
    print("Creating users table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'admin',
            created_at TEXT
        )
    ''')
    
    # Activity Log Table
    print("Creating activity_log table...")
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp TEXT,
            details TEXT
        )
    ''')
    
    # Create default admin user
    print("Creating default admin user...")
    import hashlib
    hashed_pw = hashlib.sha256("admin123".encode()).hexdigest()
    
    try:
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                 ("admin", hashed_pw, "admin", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    except sqlite3.IntegrityError:
        print("Admin user already exists")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database created successfully!")
    print("Default credentials:")
    print("  Username: admin")
    print("  Password: admin123")

if __name__ == "__main__":
    create_database()
