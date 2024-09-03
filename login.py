import streamlit as st

st.set_page_config(
        page_title="InsightView",
        layout="wide",
        page_icon=r"C:\Users\Kwaku\Desktop\project_final\logo.svg"
        
        
)

import firebase_admin
from firebase_admin import auth, credentials, initialize_app

import hashlib
import random
import smtplib
from email.mime.text import MIMEText
from streamlit_cookies_manager import EncryptedCookieManager
import requests
import json
from streamlit_lottie import st_lottie
import os
from dotenv import load_dotenv

def configure():
        load_dotenv()

def load_lottiefile(filepath:str):
    with open(filepath, "r") as f:
        return json.load(f)

lottie_video = load_lottiefile(r"Animation - 1725278038039.json")

cookie_password = os.getenv('cookie_password')
# Define a strong password for cookie encryption
cookie_password = cookie_password

# Cookie manager with password
cookies = EncryptedCookieManager(prefix="insightView", password=cookie_password)

# Ensure cookies are ready
if not cookies.ready():
    st.warning("Cookies are not ready yet. Please wait.")
    st.stop()  # Stop execution if cookies are not ready

# Access the Firebase credentials from Streamlit secrets
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

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_cred)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")
# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to generate a random 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))



def reset_password(email, new_password):
    try:
        user = auth.get_user_by_email(email)
        auth.update_user(user.uid, password=new_password)
        return True
    except Exception as e:
        st.error(f"An error occurred while resetting the password: {str(e)}")
        return False




sender_emails = os.getenv('sender_email')
sender_passwords = os.getenv('sender_password')
# Function to send OTP via email
def send_otp_email(email, otp):
    sender_email = sender_emails
    sender_password = sender_passwords
    subject = "Your OTP Verification Code"
    body = f"Insightview App. Your OTP verification code is {otp}. Please use this code to complete your registration."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = email

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send OTP: {e}")
        return False

client_ids = os.getenv('client_id')
redirect_uris = os.getenv('redirect_uri')
YOUR_FIREBASE_WEB_API_KEYS = os.getenv('YOUR_FIREBASE_WEB_API_KEY')
# Function to handle Google sign-in
def google_sign_in_button():
    client_id = client_ids
    redirect_uri = redirect_uris
    scope = 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?client_id={client_id}"
        f"&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
    )
    #st.markdown(f"""
    #    <a href="{auth_url}">
     #       <button style="background-color:#4285F4; color:white; padding:10px; border:none; border-radius:5px; cursor:pointer;">
    #            Sign in with Google
     #       </button>
    #    </a>
    #""", unsafe_allow_html=True)

client_secrets = os.getenv('client_secret')
def handle_google_auth_response():
    code = st.query_params.get('code')
    if code:
        client_id = client_ids
        client_secret = client_secrets
        redirect_uri = "http://localhost:8501/"
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        try:
            token_response = requests.post(token_url, data=token_data)
            token_json = token_response.json()
            if token_response.status_code == 200:
                access_token = token_json.get('access_token')
                if access_token:
                    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
                    user_info_params = {'access_token': access_token}
                    user_info_response = requests.get(user_info_url, params=user_info_params)
                    user_info = user_info_response.json()

                    if user_info:
                        email = user_info.get('email')
                        if email:
                            try:
                                user = auth.get_user_by_email(email)
                                st.success("Login successful")
                                cookies["logged_in"] = "True"
                                cookies["user_email"] = email
                                cookies.save()
                                st.session_state['logged_in'] = True
                                st.session_state['user_email'] = email
                            except firebase_admin.auth.UserNotFoundError:
                                st.error("User not found. Please sign up first.")
                        else:
                            st.error("Could not retrieve email from Google.")
                    else:
                        st.error("Could not retrieve user information from Google.")
                else:
                    st.error("Could not retrieve access token from Google.")
            else:
                st.error(f"Google OAuth2 token request failed with status code: {token_response.status_code}")
                st.error(f"Error response: {token_json}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
    else:
        st.error("No authorization code received from Google.")

# Check login state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = cookies.get('logged_in', default=False)
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = cookies.get('user_email', default=None)

# Logout function
def logout():
    # Clear user session
    st.session_state['logged_in'] = False
    st.session_state['user_email'] = None

    # Clear cookies
    cookies["logged_in"] = ""
    cookies["user_email"] = ""
    cookies.save()

    # Inform the user and redirect to the login page
    st.info("You have been logged out. Redirecting to the login page...")
    st.session_state['current_page'] = 'login'
    st.rerun()

# Logout button in sidebar
if st.sidebar.button("Logout", type="primary"):
    logout()

# Main app logic
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'login'

if st.session_state['current_page'] == 'login':
    if not st.session_state.get('logged_in', False):

        st.markdown('<h1 style="margin-top: -0.5rem; margin-bottom: 0;">insightView</h1>', unsafe_allow_html=True)

        # Description with smaller text
        st.markdown('<p style="font-size: 0.7rem; margin-top: 0;">Data analysis and visualization tool</p>', unsafe_allow_html=True)
      
        bigger_column_left, left_column, right_column,bigger_column_right = st.columns([2,3, 3,2])

        with left_column:
            
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")

            st_lottie(
                lottie_video,
                speed=1,
                reverse=False,
                loop=True,
                quality="low",
                height=None,
                width=None
            )

        with right_column:
            tab1, tab2 = st.tabs(["Login", "Sign Up"])
            
            with tab1:
                st.subheader("Login")
                email = st.text_input("Email:", key="login_email")
                password = st.text_input("Password:", type='password', key="login_password")
                
                if st.button("Login", key="login_page_btn", type="primary"):
                    try:
                        user = auth.get_user_by_email(email)
                        YOUR_FIREBASE_WEB_API_KEY = YOUR_FIREBASE_WEB_API_KEYS
                        sign_in_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={YOUR_FIREBASE_WEB_API_KEYS}"
                        sign_in_data = {
                            "email": email,
                            "password": password,
                            "returnSecureToken": True
                        }
                        response = requests.post(sign_in_url, json=sign_in_data)
                        
                        if response.status_code == 200:
                            st.success("Login successful")
                            cookies["logged_in"] = "True"
                            cookies["user_email"] = email
                            cookies.save()
                            st.session_state['logged_in'] = True
                            st.session_state['user_email'] = email
                            st.rerun()
                        else:
                            error_data = response.json()
                            error_message = error_data.get('error', {}).get('message', 'Unknown error')
                            st.error(f"Login failed. Error: {error_message}")
                    except auth.UserNotFoundError:
                        st.error("User not found. Please check your email or sign up.")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")

                #st.markdown("Or sign in with:")
                
                google_sign_in_button()
                st.write("")
                
                if st.button("Forgotten Password", key="forgot_password_btn", type="primary"):
                    st.session_state['current_page'] = 'forgot_password'
                    st.rerun()        

            with tab2:
                st.subheader("Sign Up")
                email = st.text_input("Email:", key="signup_email")
                password = st.text_input("Create a Password:", type='password', key="signup_password")
                otp_input = st.text_input("Enter OTP sent to your email:", key="signup_otp")

                if st.session_state.get('otp_sent') != True and st.button("Send OTP", key="send_otp_btn", type="primary"):
                    otp = generate_otp()
                    st.session_state['generated_otp'] = otp
                    st.session_state['otp_sent'] = send_otp_email(email, otp)
                    if st.session_state['otp_sent']:
                        st.success("OTP sent successfully")
                    else:
                        st.error("Failed to send OTP")

                if st.session_state.get('otp_sent') and st.button("Sign Up", key="signup_page_btn", type="primary"):
                    if otp_input == st.session_state.get('generated_otp'):
                        hashed_password = hash_password(password)
                        try:
                            user = auth.create_user(email=email, password=password)
                            st.success("Account created successfully.Proceed to Login")
                            st.session_state['current_page'] = 'login'
                        except auth.EmailAlreadyExistsError:
                            st.error("Email already exists. Please log in.")
                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
                    else:
                        st.error("Invalid OTP. Please try again.")

    else:
        # Redirect to main page if logged in
        st.session_state['current_page'] = 'main'
        st.rerun()


elif st.session_state['current_page'] == 'forgot_password':
    st.subheader("Password Reset")
    
    # Initialize session state variables if they don't exist
    if 'reset_email' not in st.session_state:
        st.session_state['reset_email'] = ''
    if 'reset_otp_sent' not in st.session_state:
        st.session_state['reset_otp_sent'] = False
    if 'otp_verified' not in st.session_state:
        st.session_state['otp_verified'] = False

    # Step 1: Enter email
    if not st.session_state['reset_otp_sent']:
        reset_email = st.text_input("Enter your registered email:", key="reset_email_input", value=st.session_state['reset_email'])
        if st.button("Send OTP", key="reset_send_otp_btn", type="primary"):
            st.session_state['reset_email'] = reset_email  # Update session state
            otp = generate_otp()
            st.session_state['reset_generated_otp'] = otp
            if send_otp_email(reset_email, otp):
                st.session_state['reset_otp_sent'] = True
                st.success("OTP sent successfully")
                st.rerun()
            else:
                st.error("Failed to send OTP")

    # Step 2: Enter OTP
    if st.session_state['reset_otp_sent'] and not st.session_state['otp_verified']:
        otp_input = st.text_input("Enter OTP sent to your email:", key="reset_otp")
        if st.button("Verify OTP", key="verify_otp_btn", type="primary"):
            if otp_input == st.session_state.get('reset_generated_otp'):
                st.session_state['otp_verified'] = True
                st.success("OTP verified successfully")
                st.rerun()
            else:
                st.error("Invalid OTP. Please try again.")

    # Step 3: Enter new password
    if st.session_state['otp_verified']:
        new_password = st.text_input("Enter new password:", type="password", key="new_password")
        confirm_password = st.text_input("Confirm new password:", type="password", key="confirm_password")
        if st.button("Reset Password", key="reset_password_btn", type="primary"):
            if new_password == confirm_password:
                if reset_password(st.session_state['reset_email'], new_password):
                    st.success("Password reset successful. Please log in with your new password.")
                    # Reset all states and redirect to login
                    st.session_state['current_page'] = 'login'
                    st.session_state['reset_email'] = ''
                    st.session_state['reset_otp_sent'] = False
                    st.session_state['otp_verified'] = False
                    st.rerun()
                else:
                    st.error("Failed to reset password. Please try again.")
            else:
                st.error("Passwords do not match. Please try again.")

    # Back to Login button
    if st.button("Back to Login", key="back_to_login_btn", type="primary"):
        st.session_state['current_page'] = 'login'
        st.session_state['reset_email'] = ''
        st.session_state['reset_otp_sent'] = False
        st.session_state['otp_verified'] = False
        st.rerun()



elif st.session_state['current_page'] == 'main':
    from main import main_page

    if __name__ == "__main__":
         main_page()
