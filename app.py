import json
import os
import random
import pandas as pd
import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ---------------------------------------------------------
# EMAIL CONFIGURATION (Read from Environment / Streamlit Secrets)
# ---------------------------------------------------------
# Local computer ya Server ki secret configuration se values fetch hongi
SENDER_EMAIL = os.getenv("SENDER_EMAIL", st.secrets.get("SENDER_EMAIL", ""))
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", st.secrets.get("SENDER_PASSWORD", ""))

def send_otp_email(receiver_email, otp_code):
    try:
        subject = "🔐 Email Verification Code - AI Timetable Studio"
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

LOGIN_BG_IMAGE = "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1920&auto=format&fit=crop"
DASHBOARD_BG_IMAGE = "https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1920&auto=format&fit=crop"

# ---------------------------------------------------------
# 2. TIMETABLE AGENT ENGINE
# ---------------------------------------------------------
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

                    timetable[day][slot] = f"📖 {subject_name}\n👨‍🏫 {teacher_name}\n📍 {room_name}"
                    pool.pop(idx)
                    daily_count += 1
                    assigned = True
                    break

                if not assigned and timetable[day][slot] == "Free":
                    timetable[day][slot] = "📚 Library Session"

        return pd.DataFrame(timetable)

# ---------------------------------------------------------
# 3. LOGIN & OTP REGISTRATION
# ---------------------------------------------------------
def login_page():
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(5, 10, 25, 0.82), rgba(5, 10, 25, 0.88)), url("{LOGIN_BG_IMAGE}");
            background-size: cover; background-position: center; background-attachment: fixed; color: #e0f7fc;
        }}
        .cyber-title {{
            font-family: 'Courier New', Courier, monospace; font-size: 2.5rem; font-weight: 800;
            text-align: center; color: #00f3ff; margin-bottom: 5px;
        }}
        div[data-testid="stColumn"] > div {{
            background: rgba(10, 20, 40, 0.8) !important; border: 1px solid rgba(0, 243, 255, 0.4) !important;
            border-radius: 12px; padding: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="cyber-title">SECURITY ACCESS</div>', unsafe_allow_html=True)
        auth_mode = st.radio("Access Level", ["🔐 LOGIN", "📝 REGISTER SYSTEM"], horizontal=True)

        if auth_mode == "🔐 LOGIN":
            username = st.text_input("USER IDENTIFIER")
            password = st.text_input("PASSCODE", type="password")

            if st.button("🚀 INITIALIZE LOGIN", use_container_width=True):
                users = st.session_state.users_db
                if username in users and users[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.user_info = {
                        "username": username,
                        "name": users[username].get("name", username),
                        "role": users[username].get("role", "Student")
                    }
                    st.success("AUTHENTICATION SUCCESSFUL")
                    st.rerun()
                else:
                    st.error("❌ ACCESS DENIED: Invalid Credentials")

        else:
            new_name = st.text_input("FULL NAME")
            new_email = st.text_input("EMAIL ADDRESS")
            new_username = st.text_input("NEW USERNAME")
            new_password = st.text_input("NEW PASSCODE", type="password")
            role = st.selectbox("ASSIGN ROLE", ["Student", "Faculty Member", "Administrator"])

            if st.button("📧 SEND VERIFICATION OTP", use_container_width=True):
                if new_username in st.session_state.users_db:
                    st.warning("⚠️ USERNAME ALREADY EXISTS")
                elif new_email and new_username and new_password and "@" in new_email:
                    otp = str(random.randint(100000, 999999))
                    with st.spinner("Sending OTP to email..."):
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
                entered_otp = st.text_input("🔑 ENTER 6-DIGIT OTP")
                if st.button("✨ VERIFY & CREATE ACCOUNT", use_container_width=True):
                    if entered_otp == st.session_state.generated_otp:
                        temp = st.session_state.temp_user_data
                        st.session_state.users_db[temp["username"]] = {
                            "password": temp["password"], "name": temp["name"],
                            "role": temp["role"], "email": temp["email"]
                        }
                        save_users(st.session_state.users_db)
                        st.session_state.generated_otp = None
                        st.session_state.temp_user_data = {}
                        st.success("🎉 EMAIL VERIFIED & USER REGISTERED SUCCESSFULLY!")
                    else:
                        st.error("❌ INVALID OTP.")

# ---------------------------------------------------------
# 4. FULL DASHBOARD APP
# ---------------------------------------------------------
def main_app():
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(rgba(10, 15, 30, 0.88), rgba(10, 15, 30, 0.92)), url("{DASHBOARD_BG_IMAGE}");
            background-size: cover; background-position: center; background-attachment: fixed; color: #f1f5f9;
        }}
        div[data-testid="stSidebar"] {{ background-color: rgba(15, 23, 42, 0.85) !important; backdrop-filter: blur(10px); }}
        </style>
    """, unsafe_allow_html=True)

    user_role = st.session_state.user_info.get('role', 'Student')
    is_student = (user_role == "Student")

    st.sidebar.markdown(f"**OPERATOR:** {st.session_state.user_info.get('name')} | `{user_role}`")
    
    if st.sidebar.button("🔴 TERMINATE SESSION"):
        st.session_state.authenticated = False
        st.session_state.user_info = {}
        st.rerun()

    st.sidebar.title("🎛️ AI CONTROLS")
    if is_student:
        st.sidebar.info("🔒 **Student Mode Active:** Controls are locked to Read-Only.")

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

    st.title("⚡ AI TIMETABLE & STUDENT MANAGEMENT STUDIO")
    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Subject Setup", "🗓️ AI Timetable Matrix", "📊 Workload Analytics", "✅ Attendance Tracker", "📝 Assignment Hub"
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
        c1.metric("Active Subjects", len(subjects_list))
        c2.metric("Weekly Classes Required", total_credits)
        c3.metric("Assigned Faculty", len(set([s["Teacher"] for s in subjects_list])) if subjects_list else 0)

        if not is_student:
            if st.button("🚀 GENERATE AI SCHEDULE", type="primary", use_container_width=True):
                subjects_info = [
                    {"name": str(r["Subject"]), "teacher": str(r["Teacher"]), "room": str(r.get("Room/Lab", "Room 101")), "credits": int(r["Weekly Classes (Credits)"])}
                    for r in subjects_list
                ]
                agent = TimetableAgent(days, time_slots, lunch_slot=lunch_break_slot)
                timetable_df = agent.generate_timetable(subjects_info, max_classes_per_day=max_classes, avoid_consecutive=avoid_consecutive)
                st.session_state["timetable_df"] = timetable_df
                st.toast("🎉 AI Timetable Generated!")

    with tab2:
        if "timetable_df" in st.session_state:
            st.subheader("🗓️ Schedule Grid")
            st.dataframe(st.session_state["timetable_df"], use_container_width=True)
        else:
            if is_student:
                st.info("ℹ️ Timetable is currently not generated by Faculty Leader.")
            else:
                st.info("👉 Tab 1 se Pehle Timetable Generate karein.")

    with tab3:
        if "timetable_df" in st.session_state:
            st.subheader("📊 Workload Metrics")
            st.write("Schedule Data Loaded successfully.")
        else:
            st.info("👉 Generate Schedule to view analytics.")

    with tab4:
        st.subheader("✅ Attendance Tracker")
        if is_student:
            st.warning("🔒 Read-Only Access")
            st.dataframe(st.session_state.attendance_data, use_container_width=True)
        else:
            st.data_editor(st.session_state.attendance_data, num_rows="dynamic", use_container_width=True)

    with tab5:
        st.subheader("📝 Assignment Records")
        if is_student:
            st.warning("🔒 Read-Only Access")
            st.dataframe(st.session_state.assignment_data, use_container_width=True)
        else:
            st.data_editor(st.session_state.assignment_data, num_rows="dynamic", use_container_width=True)

# ---------------------------------------------------------
# 5. EXECUTION ENTRY POINT
# ---------------------------------------------------------
if not st.session_state.authenticated:
    login_page()
else:
    main_app()