"""
InsightFlow – Authentication Module
Handles Login, Signup, and Logout flows using SQLite and Werkzeug password hashing.
"""

import streamlit as st
from werkzeug.security import generate_password_hash, check_password_hash
from database import create_user, get_user_by_username
from config import COLORS

def init_auth_state():
    """Initialize session state variables for authentication."""
    if "user_authenticated" not in st.session_state:
        st.session_state["user_authenticated"] = False
    if "username" not in st.session_state:
        st.session_state["username"] = None

def render_login_page():
    """Render the dual login/signup page."""
    st.markdown(
        """
        <div style="text-align: center; padding: 40px 0 20px 0;">
            <p style="font-size: 4rem; margin-bottom: 0;">📊</p>
            <h1 style="font-size: 3rem; margin: 10px 0;
                background: linear-gradient(135deg, #f0b429, #58a6ff);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;">
                InsightFlow
            </h1>
            <p style="font-size: 1.2rem; color: #8b949e; max-width: 600px; margin: 0 auto;">
                Sign in to continue to your AI-Powered Data Analytics Platform
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                st.markdown("### Welcome Back")
                l_user = st.text_input("Username", key="login_user")
                l_pass = st.text_input("Password", type="password", key="login_pass")
                submit_login = st.form_submit_button("Log In", use_container_width=True)
                
                if submit_login:
                    if not l_user or not l_pass:
                        st.error("⚠️ Please enter both username and password.")
                    else:
                        user = get_user_by_username(l_user)
                        if user and check_password_hash(user["password_hash"], l_pass):
                            st.session_state["user_authenticated"] = True
                            st.session_state["username"] = user["username"]
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password.")
                            
        with tab2:
            with st.form("signup_form"):
                st.markdown("### Create an Account")
                s_user = st.text_input("Choose a Username", key="signup_user")
                s_pass1 = st.text_input("Choose a Password", type="password", key="signup_pass1")
                s_pass2 = st.text_input("Confirm Password", type="password", key="signup_pass2")
                submit_signup = st.form_submit_button("Sign Up", use_container_width=True)
                
                if submit_signup:
                    if not s_user or not s_pass1 or not s_pass2:
                        st.error("⚠️ Please fill out all fields.")
                    elif s_pass1 != s_pass2:
                        st.error("⚠️ Passwords do not match.")
                    elif len(s_pass1) < 6:
                        st.error("⚠️ Password must be at least 6 characters.")
                    else:
                        pw_hash = generate_password_hash(s_pass1)
                        user_id = create_user(s_user, pw_hash)
                        if user_id:
                            st.success("✅ Account created! You can now log in.")
                        else:
                            st.error("❌ Username already exists. Please choose another one.")

def render_logout_button():
    """Render a logout button for the sidebar."""
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state["user_authenticated"] = False
        st.session_state["username"] = None
        # Clear data state to prevent bleeding between users (simple implementation)
        st.session_state["current_df"] = None
        st.session_state["current_df_name"] = None
        st.session_state["saved_charts"] = []
        st.rerun()
