"""
Utilities Module - Student Grade Management System
Streamlit 1.57 Compatible Version
"""

import streamlit as st
import re


def local_css():
    """Apply custom CSS styling"""

    st.markdown("""
    <style>

    /* ==========================================
       GLOBAL THEME
    ========================================== */

    .stApp {
        background-color: #f8fafc;
    }

    /* ==========================================
       HEADER
    ========================================== */

    .main-header {
        background: linear-gradient(135deg, #1e3a8a, #3b82f6);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }

    .main-header p {
        margin-top: 8px;
        opacity: 0.95;
    }

    /* ==========================================
       SIDEBAR
    ========================================== */

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #1e3a8a 0%,
            #2563eb 100%
        );
    }

    .sidebar-title {
        color: white;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        padding: 1rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.25);
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }

    section[data-testid="stSidebar"] .stRadio > div {
        gap: 6px;
    }

    section[data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.10);
        border-radius: 10px;
        padding: 10px;
        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.20);
    }

    /* ==========================================
       METRIC CARDS
    ========================================== */

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 14px;
        border-left: 5px solid #3b82f6;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }

    /* ==========================================
       BUTTONS
    ========================================== */

    .stButton > button,
    .stFormSubmitButton > button {
        background: linear-gradient(
            135deg,
            #3b82f6,
            #2563eb
        );
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        min-height: 45px;
        width: 100%;
        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 12px rgba(0,0,0,0.15);
    }

    /* ==========================================
       DOWNLOAD BUTTON
    ========================================== */

    .stDownloadButton > button {
        background: linear-gradient(
            135deg,
            #10b981,
            #059669
        );
        color: white;
        border: none;
        border-radius: 10px;
        min-height: 45px;
        width: 100%;
    }

    /* ==========================================
       INPUT FIELDS
    ========================================== */

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        border-radius: 10px !important;
    }

    /* ==========================================
       DATAFRAMES
    ========================================== */

    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }

    /* ==========================================
       EXPANDERS
    ========================================== */

    details {
        border-radius: 10px;
    }

    /* ==========================================
       ALERTS
    ========================================== */

    .stSuccess,
    .stError,
    .stWarning,
    .stInfo {
        border-radius: 10px !important;
    }

    /* ==========================================
       FILE UPLOADER
    ========================================== */

    .stFileUploader {
        border-radius: 10px;
    }

    /* ==========================================
       TABS
    ========================================== */

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
    }

    /* ==========================================
       METRICS
    ========================================== */

    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }

    /* ==========================================
       PAGE SPACING
    ========================================== */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* ==========================================
       SCROLLBAR
    ========================================== */

    ::-webkit-scrollbar {
        width: 10px;
    }

    ::-webkit-scrollbar-thumb {
        background: #94a3b8;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }

    /* ==========================================
       HIDE STREAMLIT DEFAULTS
    ========================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """, unsafe_allow_html=True)


import re

def validate_email(email):
    """
    Validate email address
    """
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    return bool(
        re.match(
            pattern,
            email.strip()
        )
    )


def format_phone_number(phone):
    """Format phone number"""

    phone = re.sub(r'\\D', '', phone)

    if phone.startswith('60'):
        phone = phone[2:]
    elif phone.startswith('0'):
        phone = phone[1:]

    if len(phone) >= 9:
        return f"+60-{phone[:2]}-{phone[2:6]}-{phone[6:]}"

    return phone


def validate_student_id(student_id):
    """Validate student ID"""

    pattern = r'^STU\\d{7}$'
    return re.match(pattern, student_id) is not None


def get_grade_color(grade):
    """Return grade color"""

    colors = {
        'A': '#10b981',
        'A-': '#34d399',
        'B+': '#3b82f6',
        'B': '#60a5fa',
        'B-': '#93c5fd',
        'C+': '#f59e0b',
        'C': '#fbbf24',
        'C-': '#fcd34d',
        'D': '#ef4444',
        'F': '#dc2626'
    }

    return colors.get(grade, '#6b7280')


def calculate_percentage(value, total):
    """Calculate percentage"""

    if total == 0:
        return 0

    return round((value / total) * 100, 2)


def format_date(date_string):
    """Format date"""

    from datetime import datetime

    try:
        date_obj = datetime.strptime(
            date_string,
            "%Y-%m-%d"
        )
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_string


def generate_student_id():
    """Generate next student ID"""

    conn = st.session_state.db_conn
    c = conn.cursor()

    c.execute(
        "SELECT student_id "
        "FROM students "
        "ORDER BY student_id DESC "
        "LIMIT 1"
    )

    result = c.fetchone()

    if result:
        last_id = result[0]
        number = int(last_id[3:]) + 1
        return f"STU{number:07d}"

    return "STU0000001"