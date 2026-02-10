import streamlit as st
import ollama
import sqlite3
import pandas as pd
from config import MODELS
from routing import classify_complexity, extract_relevant_tables, get_focused_schema


st.set_page_config(page_title="NL2SQL Toy", layout="wide")
st.title("🪄 NL2SQL Week 3")


# Sidebar
st.sidebar.title("⚙️ Settings")
mode = st.sidebar.radio("Routing Mode:", ["Auto", "Manual"])

if mode == "Manual":
    tier = st.sidebar.selectbox("Model:", ["tier1", "tier2"])
    model = MODELS[tier]
    st.sidebar.info(f"Using: {model}")
else:
    st.sidebar.info("Using smart routing")


# Input
question = st.text_input("Ask SQL question:", placeholder="top 10 customers by revenue")


if st.button("Generate SQL and execute", type="primary") and question:
    
    # Step 1: Routing (Auto mode only)
    if mode == "Auto":
        with st.spinner("🧠 Analyzing query complexity..."):
            tier, score, features = classify_complexity(question)
            model = MODELS[tier]
            
            st.info(f"**Routing:** {tier.upper()} selected (score: {score:.1f})")
            with st.expander("📊 See complexity breakdown"):
                st.json(features)
    
    # Step 2: Schema pruning
    with st.spinner("📚 Loading relevant schema..."):
        relevant_tables = extract_relevant_tables(question)
        focused_schema = get_focused_schema(relevant_tables)
        
        st.success(f"✅ Focused on: {', '.join(relevant_tables)}")
        with st.expander("🗄️ See database schema"):
            st.code(focused_schema, language="sql")
    
    # Step 3: Generate SQL
    with st.spinner(f"⚡ Generating SQL with {model}..."):
        prompt = f"""Database Schema:
{focused_schema}

Convert NL2SQL output should be just the sql code no other words:

Request: {question}

SQL:"""
        
        response = ollama.generate(model=model, prompt=prompt)
        sql = response['response'].strip()
        
        # Clean up SQL
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        st.subheader("📝 Generated SQL:")
        st.code(sql, language="sql")
    
    # Step 4: Execute SQL
    with st.spinner("🔄 Executing query..."):
        try:
            conn = sqlite3.connect('ecommerce.db')
            df = pd.read_sql_query(sql, conn)
            conn.close()
            
            st.subheader("📊 Query Result:")
            st.dataframe(df, use_container_width=True)
            st.success(f"✅ Query executed successfully! ({len(df)} rows)")
            
        except Exception as e:
            st.error(f"❌ Error executing SQL: {e}")
            st.info("💡 The SQL was generated but couldn't execute. Check the query syntax.")


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Week 3 Features:**
- ✅ Smart routing (tier1/tier2)
- ✅ Schema pruning (RAG)
- ✅ Complexity analysis
- ✅ Auto table detection
""")
