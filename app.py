import json
import os
import random
import pandas as pd
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import base64
import io

# ---------------------------------------------------------
# EMAIL CONFIGURATION
# ---------------------------------------------------------
try:
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", st.secrets.get("SENDER_EMAIL", ""))
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", st.secrets.get("SENDER_PASSWORD", ""))
except Exception:
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")

def send_otp_email(receiver_email, otp_code):
    try:
        subject = "✍ Email Verification Code - AI Timetable Studio"
        body = f"Hello,\n\nYour OTP for registration is: {otp_code}\n\nPlease do not share it."
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False

# ---------------------------------------------------------
# 1. PAGE CONFIG & DATABASE
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Timetable Studio Ultra",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "users_db.json"

def load_users():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"admin": {"password": "admin123", "name": "Admin User", "role": "Faculty Leader", "email": "admin@app.com"}}

def save_users(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
if "users_db" not in st.session_state:
    st.session_state.users_db = load_users()
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "temp_user_data" not in st.session_state:
    st.session_state.temp_user_data = {}
if "attendance_data" not in st.session_state:
    st.session_state.attendance_data = pd.DataFrame([
        {"Subject": "Python Programming", "Classes Attended": 28, "Total Classes": 32},
        {"Subject": "Database Management System", "Classes Attended": 22, "Total Classes": 30},
        {"Subject": "Web Technologies", "Classes Attended": 25, "Total Classes": 26},
        {"Subject": "Computer Networks", "Classes Attended": 18, "Total Classes": 28},
        {"Subject": "Software Engineering", "Classes Attended": 24, "Total Classes": 25},
    ])
if "assignment_data" not in st.session_state:
    st.session_state.assignment_data = pd.DataFrame([
        {"Subject": "Python Programming", "Assignment Title": "Custom Class & OOP Design", "Due Date": "2026-08-15", "Status": "Submitted", "Marks Obtained": "18/20"},
        {"Subject": "Database Management System", "Assignment Title": "ER Diagram & Normalization", "Due Date": "2026-08-18", "Status": "Pending", "Marks Obtained": "N/A"},
        {"Subject": "Web Technologies", "Assignment Title": "Responsive Portfolio with Flexbox", "Due Date": "2026-08-20", "Status": "Submitted", "Marks Obtained": "19/20"},
        {"Subject": "Computer Networks", "Assignment Title": "Subnetting & IP Configuration", "Due Date": "2026-08-22", "Status": "Pending", "Marks Obtained": "N/A"},
    ])
if "exam_data" not in st.session_state:
    st.session_state.exam_data = pd.DataFrame([
        {"Subject": "Python Programming", "Exam Date": "2026-09-10", "Time": "10:00 AM - 12:00 PM", "Room": "Lab 1", "Priority": "High"},
        {"Subject": "Database Management System", "Exam Date": "2026-09-12", "Time": "02:00 PM - 04:00 PM", "Room": "Room 201", "Priority": "Medium"},
        {"Subject": "Web Technologies", "Exam Date": "2026-09-14", "Time": "10:00 AM - 12:00 PM", "Room": "Lab 2", "Priority": "High"},
        {"Subject": "Computer Networks", "Exam Date": "2026-09-16", "Time": "02:00 PM - 04:00 PM", "Room": "Room 202", "Priority": "Medium"},
        {"Subject": "Software Engineering", "Exam Date": "2026-09-18", "Time": "10:00 AM - 12:00 PM", "Room": "Room 203", "Priority": "Low"},
    ])
if "notifications" not in st.session_state:
    st.session_state.notifications = []
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # login | register | forgot | reset
if "reset_otp" not in st.session_state:
    st.session_state.reset_otp = None
if "reset_email" not in st.session_state:
    st.session_state.reset_email = ""

LOGIN_BG_IMAGE = "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1920&auto=format&fit=crop"
DASHBOARD_BG_IMAGE = "https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1920&auto=format&fit=crop"

# ---------------------------------------------------------
# GLASSMORPHISM CSS
# ---------------------------------------------------------
GLASSMORPHISM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

body {
    background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #0f172a);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: #f1f5f9;
    font-family: 'Inter', sans-serif;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.neon-text {
    color: #00f3ff;
    text-shadow: 0 0 10px rgba(0, 243, 255, 0.6), 0 0 20px rgba(0, 243, 255, 0.4);
    font-weight: 800;
}

.glass-card {
    background: rgba(255, 255, 255, 0.07);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.glass-card:hover::before { opacity: 1; }
.glass-card:hover {
    transform: translateY(-6px) scale(1.02);
    border-color: rgba(0, 243, 255, 0.4);
    box-shadow: 0 16px 48px rgba(0, 243, 255, 0.2);
}

.login-glass-card {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(32px);
    -webkit-backdrop-filter: blur(32px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 28px;
    padding: 48px 40px;
    box-shadow: 0 24px 80px rgba(0, 0, 0, 0.5);
    max-width: 440px;
    margin: 40px auto;
    position: relative;
}
.login-glass-card::after {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(0,243,255,0.08) 0%, transparent 60%);
    animation: pulseGlow 8s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}
@keyframes pulseGlow {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.3); opacity: 0.8; }
}

.dashboard-glass {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 24px;
}
.metric-glass-card {
    background: rgba(255, 255, 255, 0.06);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    padding: 24px;
    text-align: center;
    transition: all 0.3s ease;
}
.metric-glass-card:hover {
    border-color: rgba(0, 243, 255, 0.4);
    transform: translateY(-4px);
}
.metric-glass-card h3 { color: #00f3ff; margin: 0; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
.metric-glass-card .value { font-size: 2.2rem; font-weight: 800; color: #ffffff; margin: 10px 0 0 0; }

div[data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.85) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(16px);
    border-radius: 14px;
    padding: 6px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: rgba(255, 255, 255, 0.65) !important;
    border-radius: 10px !important;
    padding: 14px 28px !important;
    transition: all 0.3s ease;
    font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: rgba(0, 243, 255, 0.18) !important;
    color: #00f3ff !important;
    border: 1px solid rgba(0, 243, 255, 0.35) !important;
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.15);
}

.stDataFrame {
    background: rgba(255, 255, 255, 0.03) !important;
    backdrop-filter: blur(14px);
    border-radius: 14px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.exam-card {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
    backdrop-filter: blur(14px);
    transition: all 0.3s ease;
}
.exam-card:hover {
    transform: translateX(6px);
    border-color: rgba(0, 243, 255, 0.3);
}
.exam-high { border-left: 5px solid #ff4757; }
.exam-medium { border-left: 5px solid #ffa502; }
.exam-low { border-left: 5px solid #2ed573; }

.stButton > button {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #ffffff;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}
.stButton > button:hover {
    background: rgba(0, 243, 255, 0.2);
    border-color: rgba(0, 243, 255, 0.5);
    color: #00f3ff;
    box-shadow: 0 0 24px rgba(0, 243, 255, 0.3);
    transform: translateY(-2px);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00f3ff 0%, #312e81 100%);
    border: none;
    color: #ffffff;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #00f3ff 0%, #1e1b4b 100%);
    box-shadow: 0 0 30px rgba(0, 243, 255, 0.4);
}

.stTextInput input, .stTextArea textarea, .stSelectbox select, .stPassword input {
    background: rgba(255, 255, 255, 0.08) !important;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.18) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    padding: 12px 16px !important;
    font-family: 'Inter', sans-serif;
}
.stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
    border-color: rgba(0, 243, 255, 0.5) !important;
    box-shadow: 0 0 16px rgba(0, 243, 255, 0.15) !important;
}

.stTextInput label, .stPassword label, .stSelectbox label {
    color: rgba(255, 255, 255, 0.7) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

.stDivider { margin: 24px 0; border-color: rgba(255, 255, 255, 0.1); }

div[data-baseweb="notification"] {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
}

.floating-deco {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none;
    z-index: -1;
    overflow: hidden;
}
.deco-blur {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.4;
    animation: floatDeco 12s ease-in-out infinite;
}
.deco-1 { top: -10%; left: -10%; width: 500px; height: 500px; background: #00f3ff; animation-delay: 0s; }
.deco-2 { bottom: -10%; right: -10%; width: 600px; height: 600px; background: #7209b7; animation-delay: -4s; }
.deco-3 { top: 30%; right: -15%; width: 400px; height: 400px; background: #f72585; animation-delay: -8s; }
@keyframes floatDeco {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(30px, -30px) scale(1.1); }
}

.stSuccess, .stError, .stWarning, .stInfo {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 12px;
}

.section-header {
    font-size: 1.3rem;
    font-weight: 700;
    color: #00f3ff;
    margin-bottom: 20px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
</style>
"""

# ---------------------------------------------------------
# 2. TIMETABLE AGENT ENGINE
# ---------------------------------------------------------
@st.cache_data
def generate_timetable_cached(subjects_tuple, days_tuple, time_slots_tuple, lunch_slot, max_classes, avoid_consecutive):
    """Cached timetable generation for performance optimization."""
    subjects_info = [{"name": s[0], "teacher": s[1], "room": s[2], "credits": s[3]} for s in subjects_tuple]
    agent = TimetableAgent(list(days_tuple), list(time_slots_tuple), lunch_slot=lunch_slot)
    return agent.generate_timetable(subjects_info, max_classes_per_day=max_classes, avoid_consecutive=avoid_consecutive)

class TimetableAgent:
    def __init__(self, days, time_slots, lunch_slot="12:00 PM - 01:00 PM"):
        self.days = days
        self.time_slots = time_slots
        self.lunch_slot = lunch_slot

    def generate_timetable(self, subjects_info, max_classes_per_day=4, avoid_consecutive=True):
        timetable = {day: {slot: "Free" for slot in self.time_slots} for day in self.days}
        pool = []
        for sub in subjects_info:
            for _ in range(sub['credits']):
                pool.append(sub)
        random.shuffle(pool)
        for day in self.days:
            if self.lunch_slot in self.time_slots:
                timetable[day][self.lunch_slot] = "🍱 LUNCH BREAK"
            daily_count = 0
            for slot in self.time_slots:
                if slot == self.lunch_slot:
                    continue
                if daily_count >= max_classes_per_day:
                    timetable[day][slot] = "⚡ Self Study / Free"
                    continue
                assigned = False
                for idx, item in enumerate(pool):
                    subject_name = item['name']
                    teacher_name = item['teacher']
                    room_name = item.get('room', 'Room 101')
                    if avoid_consecutive:
                        prev_slot_idx = self.time_slots.index(slot) - 1
                        if prev_slot_idx >= 0:
                            prev_slot = self.time_slots[prev_slot_idx]
                            if subject_name in str(timetable[day][prev_slot]):
                                continue
                    timetable[day][slot] = f"📚 {subject_name}\n👨‍🏫 {teacher_name}\n📍 {room_name}"
                    pool.pop(idx)
                    daily_count += 1
                    assigned = True
                    break
                if not assigned and timetable[day][slot] == "Free":
                    timetable[day][slot] = "📖 Library Session"
        return pd.DataFrame(timetable)

# ---------------------------------------------------------
# PDF EXPORT UTILITY
# ---------------------------------------------------------
def export_timetable_to_pdf(timetable_df, days, time_slots):
    """Generate a print-friendly HTML representation of the timetable for PDF export."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AI Timetable Export</title>
        <style>
            @page { size: A4 landscape; margin: 1cm; }
            body { font-family: 'Inter', sans-serif; background: #f1f5f9; color: #1e293b; }
            h1 { color: #0f172a; text-align: center; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #94a3b8; padding: 12px; text-align: center; font-size: 12px; }
            th { background: #0f172a; color: #f1f5f9; font-weight: 600; }
            td { background: #ffffff; }
            .lunch { background: #fef3c7 !important; color: #92400e; font-weight: 600; }
            .free { background: #f1f5f9; color: #64748b; font-style: italic; }
            .footer { margin-top: 30px; text-align: center; font-size: 10px; color: #64748b; }
        </style>
    </head>
    <body>
        <h1>⚡ AI Timetable Studio - Generated Schedule</h1>
        <table>
            <tr><th>Day / Time</th>
    """
    for slot in time_slots:
        html += f"<th>{slot}</th>"
    html += "</tr>"
    for day in days:
        html += f"<tr><th style='background:#1e1b4b;color:#fff;'>{day}</th>"
        for slot in time_slots:
            val = str(timetable_df.loc[slot, day] if slot in timetable_df.index else timetable_df.loc[day, slot] if day in timetable_df.columns else "Free")
            css_class = ""
            if "LUNCH" in val:
                css_class = "class='lunch'"
            elif "Free" in val or "Library" in val or "Self Study" in val:
                css_class = "class='free'"
            html += f"<td {css_class}>{val.replace(chr(10), '<br>')}</td>"
        html += "</tr>"
    html += """
        </table>
        <div class="footer">Generated by AI Timetable Studio - Glassmorphism UI Edition</div>
    </body>
    </html>
    """
    return html

# ---------------------------------------------------------
# SMART NOTIFICATIONS ENGINE
# ---------------------------------------------------------
def generate_smart_notifications():
    """Generate smart notifications based on assignments, attendance, and exams."""
    notifications = []
    today = datetime.now().date()

    # Assignment due reminders
    for _, row in st.session_state.assignment_data.iterrows():
        if row["Status"] == "Pending":
            try:
                due_date = datetime.strptime(str(row["Due Date"]), "%Y-%m-%d").date()
                days_left = (due_date - today).days
                if 0 <= days_left <= 3:
                    notifications.append({
                        "type": "assignment",
                        "title": f"📝 Assignment Due: {row['Assignment Title']}",
                        "message": f"Due in {days_left} day(s) for {row['Subject']}",
                        "priority": "high" if days_left <= 1 else "medium"
                    })
                elif days_left < 0:
                    notifications.append({
                        "type": "assignment",
                        "title": f"⚠️ Overdue: {row['Assignment Title']}",
                        "message": f"Was due on {row['Due Date']} for {row['Subject']}",
                        "priority": "high"
                    })
            except:
                pass

    # Attendance warnings
    for _, row in st.session_state.attendance_data.iterrows():
        try:
            attended = int(row["Classes Attended"])
            total = int(row["Total Classes"])
            if total > 0:
                percentage = (attended / total) * 100
                if percentage < 75:
                    notifications.append({
                        "type": "attendance",
                        "title": f"⚠️ Low Attendance: {row['Subject']}",
                        "message": f"Attendance at {percentage:.0f}% (below 75% threshold)",
                        "priority": "high"
                    })
        except:
            pass

    # Exam reminders
    for _, row in st.session_state.exam_data.iterrows():
        try:
            exam_date = datetime.strptime(str(row["Exam Date"]), "%Y-%m-%d").date()
            days_left = (exam_date - today).days
            if 0 <= days_left <= 3:
                notifications.append({
                    "type": "exam",
                    "title": f"🎓 Exam: {row['Subject']}",
                    "message": f"Exam on {row['Exam Date']} at {row['Time']} in {row['Room']}",
                    "priority": row["Priority"].lower()
                })
        except:
            pass

    return notifications

# ---------------------------------------------------------
# 3. LOGIN & OTP REGISTRATION
# ---------------------------------------------------------
def login_page():
    st.markdown(GLASSMORPHISM_CSS, unsafe_allow_html=True)

    # Floating decorative background
    st.markdown("""
    <div class="floating-deco">
        <div class="deco-blur deco-1"></div>
        <div class="deco-blur deco-2"></div>
        <div class="deco-blur deco-3"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
        background-size: cover; background-position: center; background-attachment: fixed; color: #f1f5f9;
    }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="login-glass-card" style="position: relative; z-index: 1;">
            <div style="text-align: center; margin-bottom: 32px; position: relative; z-index: 1;">
                <div class="neon-text" style="font-family: 'Courier New', monospace; font-size: 2.5rem; font-weight: 800;">⚡ AI TIMETABLE</div>
                <div style="font-size: 0.9rem; color: rgba(255,255,255,0.7); margin-top: 6px;">Secure Access Portal</div>
            </div>
        """, unsafe_allow_html=True)

        mode = st.session_state.auth_mode

        # ── LOGIN MODE ──
        if mode == "login":
            st.markdown('<div class="section-header">🔐 Sign In</div>', unsafe_allow_html=True)

            username = st.text_input("👤 USER IDENTIFIER", placeholder="Enter your username", key="login_user")
            password = st.text_input("🔑 PASSCODE", type="password", placeholder="Enter your password", key="login_pass")

            col_btn, col_forgot = st.columns([3, 2])
            with col_btn:
                if st.button("🚀 INITIALIZE LOGIN", use_container_width=True, type="primary", key="btn_login"):
                    users = st.session_state.users_db
                    if username in users and users[username]["password"] == password:
                        st.session_state.authenticated = True
                        st.session_state.user_info = {
                            "username": username,
                            "name": users[username].get("name", username),
                            "role": users[username].get("role", "Student"),
                            "email": users[username].get("email", "N/A")
                        }
                        st.session_state.auth_mode = "login"
                        st.success("✅ AUTHENTICATION SUCCESSFUL")
                        st.rerun()
                    else:
                        st.error("❌ ACCESS DENIED: Invalid Credentials")
            with col_forgot:
                if st.button("🔑 Forgot Password?", use_container_width=True, key="btn_forgot"):
                    st.session_state.auth_mode = "forgot"
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div style="text-align: center; color: rgba(255,255,255,0.5); font-size: 0.85rem;">New here?</div>', unsafe_allow_html=True)
            if st.button("📝 Create Account → REGISTER", use_container_width=True, key="btn_register_from_login"):
                st.session_state.auth_mode = "register"
                st.rerun()

        # ── FORGOT PASSWORD MODE (Step 1: Email) ──
        elif mode == "forgot":
            st.markdown('<div class="section-header">🔑 Reset Password</div>', unsafe_allow_html=True)
            st.markdown('<div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 20px;">Enter your registered email to receive a reset OTP.</div>', unsafe_allow_html=True)

            reset_email = st.text_input("📧 REGISTERED EMAIL", placeholder="name@example.com", key="forgot_email")

            if st.button("📤 SEND RESET OTP", use_container_width=True, type="primary", key="btn_send_reset_otp"):
                users = st.session_state.users_db
                found_user = None
                for uname, udata in users.items():
                    if udata.get("email", "").lower() == reset_email.lower():
                        found_user = uname
                        break
                if found_user:
                    otp = str(random.randint(100000, 999999))
                    with st.spinner("📤 Sending reset OTP..."):
                        if send_otp_email(reset_email, otp):
                            st.session_state.reset_otp = otp
                            st.session_state.reset_email = reset_email
                            st.session_state.reset_username = found_user
                            st.session_state.auth_mode = "reset_otp"
                            st.success(f"✅ Reset OTP sent to {reset_email}!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to send email. Please try again.")
                else:
                    st.error("❌ No account found with this email.")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Sign In", use_container_width=True, key="btn_back_login_from_forgot"):
                st.session_state.auth_mode = "login"
                st.rerun()

        # ── FORGOT PASSWORD MODE (Step 2: Verify OTP) ──
        elif mode == "reset_otp":
            st.markdown('<div class="section-header">🔑 Verify OTP</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 20px;">An OTP has been sent to <b>{st.session_state.reset_email}</b>. Enter it below.</div>', unsafe_allow_html=True)

            entered_otp = st.text_input("🔑 ENTER 6-DIGIT OTP", placeholder="123456", key="reset_otp_input")

            if st.button("✨ VERIFY OTP", use_container_width=True, type="primary", key="btn_verify_reset_otp"):
                if entered_otp == st.session_state.reset_otp:
                    st.session_state.auth_mode = "reset_pwd"
                    st.success("✅ OTP Verified! Create your new password.")
                    st.rerun()
                else:
                    st.error("❌ Invalid OTP. Please try again.")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Email", use_container_width=True, key="btn_back_forgot_from_otp"):
                st.session_state.auth_mode = "forgot"
                st.rerun()

        # ── FORGOT PASSWORD MODE (Step 3: New Password) ──
        elif mode == "reset_pwd":
            st.markdown('<div class="section-header">🔒 New Password</div>', unsafe_allow_html=True)
            st.markdown('<div style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 20px;">Set a new password for your account.</div>', unsafe_allow_html=True)

            new_pwd = st.text_input("🔑 NEW PASSCODE", type="password", placeholder="Create a new password", key="reset_new_pwd")
            confirm_pwd = st.text_input("🔑 CONFIRM PASSCODE", type="password", placeholder="Confirm your new password", key="reset_confirm_pwd")

            if st.button("💾 UPDATE PASSWORD", use_container_width=True, type="primary", key="btn_update_reset_pwd"):
                if not new_pwd or not confirm_pwd:
                    st.error("Please fill in both fields.")
                elif new_pwd != confirm_pwd:
                    st.error("Passwords do not match.")
                elif len(new_pwd) < 4:
                    st.error("Password must be at least 4 characters.")
                else:
                    username = st.session_state.get("reset_username", "")
                    if username and username in st.session_state.users_db:
                        st.session_state.users_db[username]["password"] = new_pwd
                        save_users(st.session_state.users_db)
                        st.session_state.reset_otp = None
                        st.session_state.reset_email = ""
                        st.session_state.reset_username = ""
                        st.session_state.auth_mode = "login"
                        st.success("✅ Password updated successfully! You can now sign in.")
                        st.rerun()
                    else:
                        st.error("❌ Session expired. Please start over.")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to Sign In", use_container_width=True, key="btn_back_login_from_reset"):
                st.session_state.auth_mode = "login"
                st.rerun()

        # ── REGISTER MODE ──
        elif mode == "register":
            st.markdown('<div class="section-header">📝 Create Account</div>', unsafe_allow_html=True)

            new_name = st.text_input("👤 FULL NAME", placeholder="Enter your full name", key="reg_name")
            new_email = st.text_input("📧 EMAIL ADDRESS", placeholder="name@example.com", key="reg_email")
            new_username = st.text_input("🆔 NEW USERNAME", placeholder="Choose a username", key="reg_user")
            new_password = st.text_input("🔑 NEW PASSCODE", type="password", placeholder="Create a password", key="reg_pass")
            role = st.selectbox("🎯 ASSIGN ROLE", ["Student", "Faculty Member", "Administrator"], key="reg_role")

            if st.button("📧 SEND VERIFICATION OTP", use_container_width=True, type="primary", key="btn_send_reg_otp"):
                if new_username in st.session_state.users_db:
                    st.warning("⚠️ USERNAME ALREADY EXISTS")
                elif new_email and new_username and new_password and "@" in new_email:
                    otp = str(random.randint(100000, 999999))
                    with st.spinner("📤 Sending OTP to email..."):
                        if send_otp_email(new_email, otp):
                            st.session_state.generated_otp = otp
                            st.session_state.temp_user_data = {
                                "username": new_username, "password": new_password,
                                "name": new_name, "role": role, "email": new_email
                            }
                            st.success(f"✅ OTP sent to {new_email}!")
                else:
                    st.error("Please fill all required fields correctly.")

            if st.session_state.generated_otp:
                st.divider()
                entered_otp = st.text_input("🔑 ENTER 6-DIGIT OTP", placeholder="123456", key="reg_otp_input")
                if st.button("✨ VERIFY & CREATE ACCOUNT", use_container_width=True, type="primary", key="btn_verify_reg_otp"):
                    if entered_otp == st.session_state.generated_otp:
                        temp = st.session_state.temp_user_data
                        st.session_state.users_db[temp["username"]] = {
                            "password": temp["password"], "name": temp["name"],
                            "role": temp["role"], "email": temp["email"]
                        }
                        save_users(st.session_state.users_db)
                        st.session_state.generated_otp = None
                        st.session_state.temp_user_data = {}
                        st.session_state.auth_mode = "login"
                        st.success("🎉 EMAIL VERIFIED & USER REGISTERED SUCCESSFULLY!")
                        st.rerun()
                    else:
                        st.error("❌ INVALID OTP.")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Already have an account? Sign In", use_container_width=True, key="btn_back_login_from_register"):
                st.session_state.auth_mode = "login"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. FULL DASHBOARD APP
# ---------------------------------------------------------
def main_app():
    st.markdown(GLASSMORPHISM_CSS, unsafe_allow_html=True)
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #312e81 100%);
            background-size: cover; background-position: center; background-attachment: fixed; color: #f1f5f9;
        }}
        div[data-testid="stSidebar"] {{
            background: rgba(15, 23, 42, 0.82) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    user_role = st.session_state.user_info.get('role', 'Student')
    is_student = (user_role == "Student")

    st.sidebar.markdown("""
    <div class="glass-card" style="margin-bottom: 24px;">
        <div style="color: #00f3ff; font-weight: 700;">👤 OPERATOR</div>
        <div style="font-size: 1.1rem; font-weight: 600; margin: 4px 0;">{name}</div>
        <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6);">{role}</div>
        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-top: 4px;">{email}</div>
    </div>
    """.format(name=st.session_state.user_info.get('name', 'User'), role=user_role, email=st.session_state.user_info.get('email', 'N/A')), unsafe_allow_html=True)

    if st.sidebar.button("🔴 TERMINATE SESSION", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_info = {}
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ AI CONTROLS")
    if is_student:
        st.sidebar.info("🔒 **Student Mode Active:** Controls are locked to Read-Only.")

    theme_label = "🌙 Dark Mode" if st.session_state.theme == "dark" else "☀️ Light Mode"
    if st.sidebar.button(theme_label, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    # Generate smart notifications
    if "all_notifications" not in st.session_state:
        st.session_state.all_notifications = generate_smart_notifications()
    notif_count = len(st.session_state.all_notifications)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔐 PROFILE & SETTINGS")

    with st.sidebar.expander("🔑 Change Password", expanded=False):
        old_pwd = st.text_input("Current Password", type="password", key="old_pwd")
        new_pwd = st.text_input("New Password", type="password", key="new_pwd")
        confirm_pwd = st.text_input("Confirm Password", type="password", key="confirm_pwd")
        if st.button("💾 Update Password", use_container_width=True, key="change_pwd_btn"):
            username = st.session_state.user_info.get("username", "")
            if old_pwd and new_pwd and confirm_pwd:
                if new_pwd != confirm_pwd:
                    st.error("❌ New passwords do not match!")
                elif username in st.session_state.users_db and st.session_state.users_db[username]["password"] != old_pwd:
                    st.error("❌ Current password is incorrect!")
                else:
                    st.session_state.users_db[username]["password"] = new_pwd
                    save_users(st.session_state.users_db)
                    st.success("✅ Password updated successfully!")
            else:
                st.error("Please fill all fields.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔔 SMART NOTIFICATIONS")
    if notif_count > 0:
        for n in st.session_state.all_notifications:
            pri_color = {"high": "#ff4757", "medium": "#ffa502", "low": "#2ed573"}.get(n["priority"], "#2ed573")
            st.sidebar.markdown(f"""
            <div class="glass-card" style="margin: 8px 0; padding: 12px; border-left: 4px solid {pri_color};">
                <div style="font-weight: 600; color: #00f3ff;">{n['title']}</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.8); margin-top: 2px;">{n['message']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.info("✅ All clear - no notifications!")


    shift_mode = st.sidebar.radio("⏰ OPERATING SHIFT", ["Morning Shift (9 AM - 4 PM)", "Afternoon Shift (11 AM - 6 PM)"], disabled=is_student)

    if "Morning" in shift_mode:
        time_slots = ["09:00 AM - 10:00 AM", "10:00 AM - 11:00 AM", "11:00 AM - 12:00 PM", "12:00 PM - 01:00 PM", "01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM", "03:00 PM - 04:00 PM"]
        default_lunch = "12:00 PM - 01:00 PM"
    else:
        time_slots = ["11:00 AM - 12:00 PM", "12:00 PM - 01:00 PM", "01:00 PM - 02:00 PM", "02:00 PM - 03:00 PM", "04:00 PM - 05:00 PM", "05:00 PM - 06:00 PM"]
        default_lunch = "02:00 PM - 03:00 PM"

    lunch_break_slot = st.sidebar.selectbox("🍱 LUNCH SLOT", time_slots, index=time_slots.index(default_lunch), disabled=is_student)
    max_classes = st.sidebar.slider("🔥 MAX CLASSES / DAY", min_value=2, max_value=6, value=4, disabled=is_student)
    avoid_consecutive = st.sidebar.toggle("Avoid Back-to-Back Same Subject", value=True, disabled=is_student)
    include_saturday = st.sidebar.toggle("Include Saturday Classes", value=True, disabled=is_student)

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    if include_saturday:
        days.append("Saturday")

    st.markdown("""
    <div class="glass-card" style="margin-bottom: 24px;">
        <h1 style="margin: 0; color: #00f3ff; font-size: 2.5rem;">⚡ AI TIMETABLE & STUDENT MANAGEMENT STUDIO</h1>
        <p style="margin: 8px 0 0 0; color: rgba(255,255,255,0.7);">Glassmorphism UI • Smart Features • Student Management</p>
    </div>
    """, unsafe_allow_html=True)

    # Notification bell
    if notif_count > 0:
        st.warning(f"𔔧 {notif_count} Smart Notification(s) - Check sidebar for details!")
    else:
        st.info("✅ No pending notifications. All good!")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Subject Setup", "🗓️ AI Timetable Matrix", "📊 Workload Analytics", "✅ Attendance Tracker", "📝 Assignment Hub", "🎓 Exam Schedule"
    ])

    default_data = pd.DataFrame([
        {"Subject": "Python Programming", "Teacher": "Dr. Raza Sir", "Room/Lab": "Lab 1", "Weekly Classes (Credits)": 4},
        {"Subject": "Database Management System", "Teacher": "Prof. Kazmi Sir", "Room/Lab": "Room 201", "Weekly Classes (Credits)": 4},
        {"Subject": "Web Technologies", "Teacher": "Er. Saurabh Sir", "Room/Lab": "Lab 2", "Weekly Classes (Credits)": 3},
        {"Subject": "Computer Networks", "Teacher": "Dr. Muskan Ma'am", "Room/Lab": "Room 202", "Weekly Classes (Credits)": 3},
        {"Subject": "Software Engineering", "Teacher": "Prof. Rakesh Sir", "Room/Lab": "Room 203", "Weekly Classes (Credits)": 3},
        {"Subject": "Python Lab", "Teacher": "Dr. Farzan Sir", "Room/Lab": "Lab 1", "Weekly Classes (Credits)": 2},
    ])

    with tab1:
        st.markdown('<div class="dashboard-glass">', unsafe_allow_html=True)
        st.subheader("⚙️ Subject & Venue Configuration")
        if is_student:
            st.warning("🔒 Read-Only Access: Students cannot modify subjects or regenerate timetables.")
            st.dataframe(default_data, use_container_width=True)
            subjects_list = [row for _, row in default_data.iterrows()]
        else:
            edited_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True, key="subject_editor_v10")
            subjects_list = [row for _, row in edited_df.iterrows() if row["Subject"] and row["Teacher"]]

        total_credits = sum([int(s["Weekly Classes (Credits)"]) for s in subjects_list]) if subjects_list else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-glass-card">
                <h3>Active Subjects</h3>
                <div class="value">{len(subjects_list)}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-glass-card">
                <h3>Weekly Classes</h3>
                <div class="value">{total_credits}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-glass-card">
                <h3>Assigned Faculty</h3>
                <div class="value">{len(set([s["Teacher"] for s in subjects_list])) if subjects_list else 0}</div>
            </div>
            """, unsafe_allow_html=True)

        if not is_student:
            if st.button("🚀 GENERATE AI SCHEDULE", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is generating your timetable..."):
                    subjects_info_tuples = [
                        (str(r["Subject"]), str(r["Teacher"]), str(r.get("Room/Lab", "Room 101")), int(r["Weekly Classes (Credits)"]))
                        for r in subjects_list
                    ]
                    timetable_df = generate_timetable_cached(
                        tuple(subjects_info_tuples),
                        tuple(days),
                        tuple(time_slots),
                        lunch_break_slot,
                        max_classes,
                        avoid_consecutive
                    )
                    st.session_state["timetable_df"] = timetable_df
                    st.toast("🎉 AI Timetable Generated!")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="dashboard-glass">', unsafe_allow_html=True)
        st.subheader("🗓️ Schedule Grid")
        if "timetable_df" in st.session_state:
            st.dataframe(st.session_state["timetable_df"], use_container_width=True)
            st.markdown("### 📤 Export Options")
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            with col_exp1:
                csv = st.session_state["timetable_df"].to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export CSV",
                    data=csv,
                    file_name="ai_timetable.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_exp2:
                html_export = export_timetable_to_pdf(
                    st.session_state["timetable_df"], days, time_slots
                )
                st.download_button(
                    label="🖨️ Export HTML (Print/PDF)",
                    data=html_export.encode('utf-8'),
                    file_name="ai_timetable.html",
                    mime="text/html",
                    use_container_width=True
                )
            with col_exp3:
                if st.button("🖨️ Print Friendly View", use_container_width=True):
                    st.session_state["show_print"] = True
                    st.info("🖨️ Use Ctrl+P to print this page as PDF")
        else:
            if is_student:
                st.info("ℹ️ Timetable is currently not generated by Faculty Leader.")
            else:
                st.info("👉 Go to Tab 1 and Generate Timetable first.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="dashboard-glass">', unsafe_allow_html=True)
        st.subheader("📊 Workload Analytics")
        if "timetable_df" in st.session_state:
            df = st.session_state["timetable_df"]
            total_slots = df.size
            free_slots = (df == "Free").sum().sum() + (df == "⚡ Self Study / Free").sum().sum() + (df == "📖 Library Session").sum().sum()
            busy_slots = total_slots - free_slots
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown(f"""
                <div class="metric-glass-card">
                    <h3>Total Slots</h3>
                    <div class="value">{total_slots}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="metric-glass-card">
                    <h3>Busy Slots</h3>
                    <div class="value">{busy_slots}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_c:
                utilization = round((busy_slots / total_slots) * 100, 1) if total_slots > 0 else 0
                st.markdown(f"""
                <div class="metric-glass-card">
                    <h3>Utilization</h3>
                    <div class="value">{utilization}%</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### 📈 Daily Class Distribution")
            daily_counts = {}
            for day in df.columns:
                count = 0
                for slot in df.index:
                    val = str(df.loc[slot, day])
                    if not any(x in val for x in ["Free", "Self Study", "Library", "LUNCH"]):
                        count += 1
                daily_counts[day] = count
            chart_df = pd.DataFrame(list(daily_counts.items()), columns=["Day", "Classes"])
            st.bar_chart(chart_df.set_index("Day"))

            st.markdown("### 📋 Full Schedule Matrix")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("👉 Generate Schedule to view analytics.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="dashboard-glass">', unsafe_allow_html=True)
        st.subheader("✅ Attendance Tracker")
        if is_student:
            st.warning("🔒 Read-Only Access")
            st.dataframe(st.session_state.attendance_data, use_container_width=True)
        else:
            st.data_editor(st.session_state.attendance_data, num_rows="dynamic", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab5:
        st.markdown('<div class="dashboard-glass">', unsafe_allow_html=True)
        st.subheader("📝 Assignment Records")
        if is_student:
            st.warning("🔒 Read-Only Access")
            st.dataframe(st.session_state.assignment_data, use_container_width=True)
        else:
            st.data_editor(st.session_state.assignment_data, num_rows="dynamic", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab6:
        st.markdown('<div class="dashboard-glass">', unsafe_allow_html=True)
        st.subheader("🎓 Exam Schedule")
        st.dataframe(st.session_state.exam_data, use_container_width=True)
        st.markdown("""
        <div class="glass-card" style="margin-top: 20px;">
            <h4 style="color: #00f3ff; margin-top: 0;">📅 Upcoming Exams</h4>
            <p style="color: rgba(255,255,255,0.7);">Track your exam dates and prepare accordingly.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. EXECUTION ENTRY POINT
# ---------------------------------------------------------
if not st.session_state.authenticated:
    login_page()
else:
    main_app()