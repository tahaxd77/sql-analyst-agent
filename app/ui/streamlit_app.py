import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
import streamlit as st
from app.agent.graph import agent_executor
from app.database.connection import get_db_schema

st.set_page_config(page_title="Self-Correcting SQL Analyst", layout="wide")
st.title("Autonomous SQL Analyst Agent")
st.markdown("Natural Language to SQL with AST Security Guardrails & Reflexion Loops")

if "session_id" not in st.session_state:
    st.session_state.session_id = "demo-session-001"

question = st.text_input("Enter your business query:", placeholder="e.g., Which customer spent the most money overall?")

if st.button("Run Analysis", type="primary") and question:
    with st.spinner("Agent reasoning and validating query..."):
        config = {"configurable": {"thread_id": st.session_state.session_id}}
        result = agent_executor.invoke({
            "question": question,
            "schema": get_db_schema(),
            "is_relevant": None,
            "sql_query": None,
            "query_result": None,
            "error_message": None,
            "retry_count": 0,
            "final_answer": None
        }, config=config)

        st.subheader("Final Answer")
        st.write(result["final_answer"])

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Self-Correction Retries", result["retry_count"])
            st.subheader("Executed SQL Query")
            st.code(result["sql_query"], language="sql")

        with col2:
            st.subheader("Retrieved Records")
            if result["query_result"]:
                st.dataframe(result["query_result"])
            else:
                st.info("No records returned.")