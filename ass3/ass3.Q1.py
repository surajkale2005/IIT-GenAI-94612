import streamlit as st
import pandas as pd
from pandasql import sqldf

st.title("CSV SQL Query Executor")

# Upload CSV
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 CSV Preview")
    st.dataframe(df)

    st.info("Table name for SQL queries is: **df**")

    # SQL query input
    query = st.text_area(
        "Enter SQL Query",
        value="SELECT * FROM df LIMIT 5"
    )

    if st.button("Run Query"):
        try:
            result = sqldf(query, {"df": df})
            st.subheader("Query Result")
            st.dataframe(result)
        except Exception as e:
            st.error(f"Error: {e}")

