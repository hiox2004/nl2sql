import streamlit as st
import ollama
import sqlite3
import pandas as pd
from config import MODELS


st.set_page_config(page_title="NL2SQL Toy", layout="wide")
st.title(" NL2SQL Week 1")

# Sidebar
tier = st.sidebar.selectbox("Model:", ["tier1", "tier2"])
model = MODELS[tier]
st.sidebar.info(f"Using: {model}")

# Input
question = st.text_input("Ask SQL question:", placeholder="top 10 customers by revenue")

if st.button("Generate SQL and exectute") and question:
    with st.spinner("Converting to SQL..."):
        prompt = f"You are an SQL expert. Your task is to create a SQL query for the following request in NL form, the output should be a valid SQL query and only that, no other words should be used. JUST THE SQL CODE: {question}\nSQL:"
        response = ollama.generate(model=model, prompt=prompt)
        sql = response['response'].strip()
        
        st.subheader("Generated SQL:")
        st.code(sql, language="sql")
        
    with st.spinner("Executing SQL..."):
        try:
            conn = sqlite3.connect('ecommerce.db')
            df =pd.read_sql_query(sql, conn)
            conn.close()
            st.subheader("Query Result:")
            st.dataframe(df, use_container_width=True)
            st.success("Query executed successfully!")
        except Exception as e:
            st.error(f"Error executing SQL: {e}")