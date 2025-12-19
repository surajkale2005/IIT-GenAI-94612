import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="CSV Explorer App", layout="centered")


USERS_FILE = "users.csv"
HISTORY_FILE = "userfiles.csv"


if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["userid", "password"]).to_csv(USERS_FILE, index=False)

if not os.path.exists(HISTORY_FILE):
    pd.DataFrame(columns=["userid", "filename", "upload_time"]).to_csv(HISTORY_FILE, index=False)


if "user" not in st.session_state:
    st.session_state.user = None


def authenticate(uid, pwd):
    df = pd.read_csv(USERS_FILE)
    return not df[(df.userid == uid) & (df.password == pwd)].empty

def user_exists(uid):
    df = pd.read_csv(USERS_FILE)
    return uid in df.userid.values


st.sidebar.title("Menu")

if st.session_state.user is None:
    menu = st.sidebar.radio("Navigate", ["Home", "Login", "Register"])
else:
    menu = st.sidebar.radio(
        "Navigate",
        ["Explore CSV", "See History", "Logout"]
    )


if menu == "Home":
    st.title("Home")
    st.write("Welcome to the **CSV Explorer App**")
    st.write("Register or Login to upload and explore CSV files.")


elif menu == "Register":
    st.title("Register")

    with st.form("register_form"):
        uid = st.text_input("User ID")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")

    if submit:
        if not uid or not pwd:
            st.error("All fields are required")
        elif user_exists(uid):
            st.error("User already exists")
        else:
            df = pd.read_csv(USERS_FILE)
            df.loc[len(df)] = [uid, pwd]
            df.to_csv(USERS_FILE, index=False)
            st.success("Registration successful! Please login.")


elif menu == "Login":
    st.title("Login")

    with st.form("login_form"):
        uid = st.text_input("User ID")
        pwd = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        if authenticate(uid, pwd):
            st.session_state.user = uid
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid User ID or Password")


elif menu == "Explore CSV":
    st.title("Explore CSV")
    st.write(f"Welcome, **{st.session_state.user}**")

    file = st.file_uploader("Upload CSV file", type="csv")

    if file:
        df = pd.read_csv(file)
        st.subheader("CSV Preview")
        st.dataframe(df)

        history = pd.read_csv(HISTORY_FILE)
        history.loc[len(history)] = [
            st.session_state.user,
            file.name,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        history.to_csv(HISTORY_FILE, index=False)

        st.success("File uploaded & history saved")


elif menu == "See History":
    st.title("Upload History")

    history = pd.read_csv(HISTORY_FILE)
    user_history = history[history.userid == st.session_state.user]

    if user_history.empty:
        st.info("No uploads found")
    else:
        st.dataframe(user_history)


elif menu == "Logout":
    st.session_state.user = None
    st.success("Logged out successfully")
    st.rerun()
