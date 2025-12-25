import streamlit as st
import pandas as pd
from pandasql import sqldf
import requests
import json
import time
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# -----------------------------
# Streamlit Page Setup
# -----------------------------
st.set_page_config(page_title="Multi-Agent App", layout="wide")
st.title("🧠 Multi-Agent Intelligent Application")

# -----------------------------
# Sidebar Agent Selection
# -----------------------------
st.sidebar.title("Agent Selection")
agent_choice = st.sidebar.selectbox(
    "Choose Agent",
    ["CSV Question Answering Agent", "Sunbeam Internship Agent"]
)

# -----------------------------
# Chat History (SAFE FORMAT)
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# Utility: Call LM Studio
# -----------------------------
def call_llm(prompt):
    url = "http://127.0.0.1:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    data = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant. Explain answers in simple English."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()
    return result["choices"][0]["message"]["content"]

# =====================================================
# AGENT 1: CSV QUESTION ANSWERING AGENT
# =====================================================
if agent_choice == "CSV Question Answering Agent":
    st.header("📊 CSV Question Answering Agent")

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("📄 CSV Preview")
        st.dataframe(df)

        st.subheader("📌 CSV Schema")
        schema_text = "\n".join([f"{col} : {dtype}" for col, dtype in df.dtypes.items()])
        st.code(schema_text)

        user_query = st.chat_input("Ask a question about the CSV data")

        if user_query:
            st.session_state.chat_history.append({"role": "user", "content": user_query})

            try:
                prompt = f"""
                CSV Columns:
                {schema_text}

                User Question:
                {user_query}

                Convert the question into an SQL query for table name df.
                Only return SQL.
                """

                sql_query = call_llm(prompt)

                result_df = sqldf(sql_query, {"df": df})

                answer = f"""
**SQL Used:**
```sql
{sql_query}
