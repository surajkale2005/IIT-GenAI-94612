import streamlit as st
import pandas as pd
from pandasql import sqldf
import time
import os
import re
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from langchain.chat_models import init_chat_model

load_dotenv()


llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)


st.set_page_config(page_title="Multi-Agent System", layout="wide")
st.title("Intelligent Multi-Agent Application")


st.sidebar.title("Agent Selection")
agent_choice = st.sidebar.selectbox(
    "Choose Agent",
    ["CSV Question Answering Agent", "Sunbeam Internship Agent"]
)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def show_chat():
    for chat in st.session_state.chat_history:
        if chat["role"] == "user":
            st.chat_message("user").write(chat["content"])
        else:
            st.chat_message("assistant").write(chat["content"])


@st.cache_data(show_spinner=True)
def scrape_sunbeam():
    URL = "https://www.sunbeaminfo.in/internship"
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get(URL)
    wait = WebDriverWait(driver, 15)

    try:
        panels = driver.find_elements(By.CSS_SELECTOR, "a[data-toggle='collapse']")
        for panel in panels:
            driver.execute_script("arguments[0].click();", panel)
            time.sleep(1)
    except:
        pass

    data = {}
    try:
        main_content = driver.find_element(By.CSS_SELECTOR, "#accordion")
        data["overview"] = main_content.text.strip() or "Overview not available."
    except:
        data["overview"] = "Overview not available."

    try:
        tech_elements = driver.find_elements(By.CSS_SELECTOR, "#collapseTwo li")
        data["technologies"] = [t.text.strip() for t in tech_elements if t.text.strip()]
    except:
        data["technologies"] = []

    try:
        rows = driver.find_elements(By.CSS_SELECTOR, "#collapseSix table tr")[1:]
        batches = []
        for r in rows:
            cols = r.find_elements(By.TAG_NAME, "td")
            batches.append(" | ".join(c.text.strip() for c in cols))
        data["batches"] = batches
    except:
        data["batches"] = []

    driver.quit()
    return data


if agent_choice == "CSV Question Answering Agent":
    st.subheader("CSV Question Answering Agent")

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("CSV Preview")
        st.dataframe(df.head())
        st.subheader("CSV Schema")
        st.code(df.dtypes.to_string())

        question = st.text_input("Ask anything about this CSV")

        if st.button("Get Answer") and question:
            st.session_state.chat_history.append({"role": "user", "content": question})

            
            with st.spinner("Generating SQL query..."):
                sql_prompt = f"""
You are a SQL expert. Table name is 'data'.
Table schema:
{df.dtypes}

Question:
{question}

Instruction:
- Write a valid SQLite SQL query
- Output ONLY SQL
- Use table name as 'data'
- If not possible, output Error
                """
                sql_response = llm.invoke(sql_prompt)
                sql_query = sql_response.content.strip()

            st.subheader("Generated SQL Query")
            st.code(sql_query, language="sql")

            
            if sql_query.lower() == "error":
                st.error("Could not generate SQL for this question.")
            else:
                try:
                    result_df = sqldf(sql_query, {"data": df})
                    st.subheader("Query Result")
                    st.dataframe(result_df)

                    # Explanation
                    with st.spinner("Explaining the result..."):
                        explain_prompt = f"""
Explain the following SQL query result in VERY SIMPLE English.
Assume the reader is a beginner.
Use short sentences.

Question:
{question}

Result:
{result_df.to_string(index=False)}
                        """
                        explanation = llm.invoke(explain_prompt)

                    st.subheader("Simple Explanation")
                    st.success(explanation.content)

                    st.session_state.chat_history.append({"role": "assistant", "content": explanation.content})

                except Exception as e:
                    st.error("Error while executing SQL on CSV")
                    st.code(str(e))

    show_chat()


elif agent_choice == "Sunbeam Internship Agent":
    st.subheader("Sunbeam Internship Agent")
    sunbeam_data = scrape_sunbeam()

    question = st.chat_input("Ask about Sunbeam internships")

    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        q = question.lower()

        if "overview" in q or "internship" in q:
            answer = sunbeam_data["overview"]
        elif "technology" in q or "course" in q:
            answer = "Available technologies:\n\n" + "\n".join(sunbeam_data["technologies"])
        elif "batch" in q or "date" in q or "top" in q or "internships" in q:
            top_internships = sunbeam_data["batches"][:5]
            if top_internships:
                answer = "Top Sunbeam Internships:\n\n" + "\n".join(top_internships)
            else:
                answer = "No internship batches found."
        else:
            answer = (
                "I collected internship data from the Sunbeam website.\n"
                "You can ask about overview, technologies, or top internships."
                "explain in simpole english."
                "find the best possible answer from the given question." 
                )

        final_answer = (
            "I first scraped the Sunbeam website.\n\n"
            "Then I answered your question using the collected data.\n\n" + answer
        )

        st.session_state.chat_history.append({"role": "assistant", "content": final_answer})

    show_chat()
