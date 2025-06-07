import streamlit as st

# Ensure environment variables are loaded
from dotenv import load_dotenv
load_dotenv()

import os
import json
import random
import hashlib
import smtplib
import requests
from email.mime.text import MIMEText
from streamlit_cookies_manager import EncryptedCookieManager
from streamlit_lottie import st_lottie
import firebase_admin
from firebase_admin import auth, credentials

# Firebase config from secrets
firebase_cred = {
    "type": st.secrets["Firebase_cred"]["firebase.json.type"],
    "project_id": st.secrets["Firebase_cred"]["firebase.json.project_id"],
    "private_key_id": st.secrets["Firebase_cred"]["firebase.json.private_key_id"],
    "private_key": st.secrets["Firebase_cred"]["firebase.json.private_key"],
    "client_email": st.secrets["Firebase_cred"]["firebase.json.client_email"],
    "client_id": st.secrets["Firebase_cred"]["firebase.json.client_id"],
    "auth_uri": st.secrets["Firebase_cred"]["firebase.json.auth_uri"],
    "token_uri": st.secrets["Firebase_cred"]["firebase.json.token_uri"],
    "auth_provider_x509_cert_url": st.secrets["Firebase_cred"]["firebase.json.auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["Firebase_cred"]["firebase.json.client_x509_cert_url"],
    "universe_domain": st.secrets["Firebase_cred"]["firebase.json.universe_domain"]
}

# Initialize Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_cred)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase init error: {e}")
        st.stop()

# UI config
st.set_page_config(
    page_title="InsightView",
    layout="wide",
    page_icon="logo.svg"  # Ensure this file is in the root dir or adjust path
)

# Load animation
try:
    with open("Animation - 1725278038039.json") as f:
        lottie_video = json.load(f)
except Exception:
    lottie_video = None

# Cookie manager setup
from streamlit_cookies_manager import CookieManager
cookies = CookieManager(prefix="insightView")


# Utilities

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    sender_email = os.getenv("sender_email")
    sender_password = os.getenv("sender_password")
    msg = MIMEText(f"Insightview OTP: {otp}")
    msg["Subject"] = "Your OTP Verification Code"
    msg["From"] = sender_email
    msg["To"] = email
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"OTP Email Error: {e}")
        return False

def reset_password(email, new_pw):
    try:
        user = auth.get_user_by_email(email)
        auth.update_user(user.uid, password=new_pw)
        return True
    except Exception as e:
        st.error(f"Password reset error: {e}")
        return False

# Auth state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = cookies.get('logged_in') == 'True'
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = cookies.get('user_email', None)

# Logout
if st.sidebar.button("Logout"):
    cookies["logged_in"] = ""
    cookies["user_email"] = ""
    cookies.save()
    st.session_state['logged_in'] = False
    st.session_state['user_email'] = None
    st.rerun()

# Pages
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'login'

# Import your pages
import home, data_visualization, query_data, sentimental_analysis
import text_summarization, data_preprocessing, tabular_data_summarization

def show_main_app():
    st.markdown("<h1>insightView</h1><p style='font-size:0.8rem'>Data analysis and visualization tool</p>", unsafe_allow_html=True)
    tabs = st.tabs([
        "Upload Data", "Data Preprocessing", "Tabular Data Summarization",
        "Data Visualization", "Query your media", "Text Summarization", "Sentimental Analysis"
    ])
    with tabs[0]: home.home()
    with tabs[1]: data_preprocessing.data_preprocessing()
    with tabs[2]: tabular_data_summarization.tabular_data_summarization()
    with tabs[3]: data_visualization.data_visualization()
    with tabs[4]: query_data.query_data()
    with tabs[5]: text_summarization.text_summarization()
    with tabs[6]: sentimental_analysis.sentimental_analysis()

# Login page logic
if st.session_state['current_page'] == 'login':
    if not st.session_state['logged_in']:
        # Login/Signup UI
        st.title("insightView")
        st_lottie(lottie_video, speed=1) if lottie_video else None

        tab1, tab2 = st.tabs(["Login", "Sign Up"])

        with tab1:
            email = st.text_input("Email:", key="login_email")
            pw = st.text_input("Password:", type="password", key="login_password")
            if st.button("Login"):
                try:
                    auth.get_user_by_email(email)  # Check user exists
                    resp = requests.post(
                        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={os.getenv('YOUR_FIREBASE_WEB_API_KEY')}",
                        json={"email": email, "password": pw, "returnSecureToken": True}
                    )
                    if resp.status_code == 200:
                        cookies["logged_in"] = "True"
                        cookies["user_email"] = email
                        cookies.save()
                        st.session_state['logged_in'] = True
                        st.session_state['user_email'] = email
                        st.rerun()
                    else:
                        st.error("Login failed. Check credentials.")
                except:
                    st.error("Login error. User not found.")

        with tab2:
            email = st.text_input("Email:", key="signup_email")
            pw = st.text_input("Create Password:", type="password", key="signup_password")
            otp_input = st.text_input("Enter OTP:", key="signup_otp")

            if st.button("Send OTP"):
                otp = generate_otp()
                st.session_state['generated_otp'] = otp
                if send_otp_email(email, otp):
                    st.success("OTP sent.")
                else:
                    st.error("OTP failed.")

            if st.button("Sign Up"):
                if otp_input == st.session_state.get('generated_otp'):
                    try:
                        auth.create_user(email=email, password=pw)
                        st.success("Account created. Please log in.")
                    except:
                        st.error("Signup failed.")
                else:
                    st.error("Invalid OTP.")

        if st.button("Forgotten Password"):
            st.session_state['current_page'] = 'forgot_password'
            st.rerun()
    else:
        st.session_state['current_page'] = 'main'
        st.rerun()

# Forgot password page
elif st.session_state['current_page'] == 'forgot_password':
    st.subheader("Reset Password")
    email = st.text_input("Email")
    if st.button("Send OTP"):
        otp = generate_otp()
        st.session_state['reset_otp'] = otp
        st.session_state['reset_email'] = email
        if send_otp_email(email, otp):
            st.success("OTP sent.")

    otp_input = st.text_input("Enter OTP")
    if st.button("Verify OTP"):
        if otp_input == st.session_state.get('reset_otp'):
            st.session_state['otp_verified'] = True
            st.success("OTP verified")

    if st.session_state.get('otp_verified'):
        pw1 = st.text_input("New Password", type="password")
        pw2 = st.text_input("Confirm Password", type="password")
        if pw1 == pw2 and pw1:
            if reset_password(st.session_state['reset_email'], pw1):
                st.success("Password reset. Login now.")
                st.session_state['current_page'] = 'login'
                st.rerun()
        else:
            st.error("Passwords don't match")

    if st.button("Back to Login"):
        st.session_state['current_page'] = 'login'
        st.rerun()

# Main app
elif st.session_state['current_page'] == 'main':
    show_main_app()
