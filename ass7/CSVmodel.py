import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from pandasql import sqldf
from langchain.chat_models import init_chat_model


load_dotenv()


llm = init_chat_model(
    model="llama-3.3-70b-versatile",
    model_provider="openai",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)


st.set_page_config(page_title="CSV Question Answering using SQL + LLM")
st.title("Ask Questions on CSV (Get Real Answers)")

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("CSV Preview")
    st.dataframe(df.head())

    st.subheader("CSV Schema")
    st.code(df.dtypes.to_string())

    question = st.text_input("Ask anything about this CSV")

    if st.button("Get Answer") and question:
        
        with st.spinner("Generating SQL query..."):
            sql_prompt = f"""
            You are a SQLite expert.

            Table name: data
            Table schema:
            {df.dtypes}

            Question:
            {question}

            Instruction:
            - Write a valid SQLite SQL query
            - Output ONLY SQL
            - Use table name as data
            - If not possible, output Error
            """

            sql_response = llm.invoke(sql_prompt)
            sql_query = sql_response.content.strip()

        st.subheader("Generated SQL")
        st.code(sql_query, language="sql")

        if sql_query.lower() == "error":
            st.error("Could not generate SQL for this question.")
        else:
            
            try:
                result_df = sqldf(sql_query, {"data": df})

                st.subheader("Query Result (Actual Answer from CSV)")
                st.dataframe(result_df)

                
                with st.spinner("Explaining the answer..."):
                    explain_prompt = f"""
                    Explain the following result in VERY SIMPLE English.
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

            except Exception as e:
                st.error("⚠️ Error while executing SQL on CSV")
                st.code(str(e))

else:
    st.info("⬆️ Please upload a CSV file to continue")
