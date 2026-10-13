# agent.py
import sqlite3
from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

# --- 1. Graph State Definition ---
class AgentState(TypedDict):
    question: str
    schema: str
    sql_query: Optional[str]
    query_result: Optional[List[Dict[str, Any]]]
    error_message: Optional[str]
    retry_count: int
    final_answer: Optional[str]

# --- 2. Database Helper Functions ---
def get_db_schema() -> str:
    """Extracts tables and column definitions from SQLite."""
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()
    conn.close()
    return "\n\n".join([f"Table Schema for {name}:\n{sql}" for name, sql in tables])

def run_query(sql: str) -> tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """Executes SQL query safely; returns (results, error)."""
    # Guard against accidental destructive queries
    cleaned_sql = sql.strip().upper()
    if any(cleaned_sql.startswith(verb) for verb in ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "ALTER"]):
        return None, "Write and destructive operations (DROP/DELETE/INSERT/UPDATE) are strictly forbidden."

    try:
        conn = sqlite3.connect("store.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return result, None
    except sqlite3.Error as e:
        return None, str(e)
class SQLOutput(BaseModel):
    sql_query: str = Field(description="The executable SQLite query.")
    reasoning: str = Field(description="Brief explanation of table joins and filters applied.")
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0
)
structured_sql_llm = llm.with_structured_output(SQLOutput)

def generate_sql(state: AgentState) -> Dict[str, Any]:
    """Generates initial SQL from question and schema."""
    prompt = f"""You are an expert SQL engineer. Given the SQLite database schema below, write a clean SQL query to answer the user's question.

Schema:
{state['schema']}

User Question: {state['question']}
"""
    response: SQLOutput = structured_sql_llm.invoke([
        SystemMessage(content="Return strictly valid SQLite queries."),
        HumanMessage(content=prompt)
    ])
    return {
        "sql_query": response.sql_query,
        "error_message": None
    }

def execute_sql(state: AgentState) -> Dict[str, Any]:
    """Runs query and captures either the recordset or error message."""
    sql = state["sql_query"]
    results, error = run_query(sql)
    return {
        "query_result": results,
        "error_message": error
    }

def self_correct_sql(state: AgentState) -> Dict[str, Any]:
    """Analyzes the error message and generates a corrected query."""
    prompt = f"""Your previous SQLite query failed with an execution error.

Schema:
{state['schema']}

Original User Question:
{state['question']}

Failed SQL Query:
{state['sql_query']}

Database Error:
{state['error_message']}

Diagnose the cause (e.g., column misspellings, missing joins, invalid dialect syntax) and write a corrected query.
"""
    response: SQLOutput = structured_sql_llm.invoke([
        SystemMessage(content="You are a SQL debugger. Fix the failed query."),
        HumanMessage(content=prompt)
    ])
    return {
        "sql_query": response.sql_query,
        "retry_count": state["retry_count"] + 1,
        "error_message": None
    }

def synthesize_answer(state: AgentState) -> Dict[str, Any]:
    """Formats the data result or informs user if queries exhausted retries."""
    if state["error_message"]:
        answer = f"Could not answer query after {state['retry_count']} retry attempts. Error: {state['error_message']}"
    else:
        prompt = f"""Answer the user's question using the retrieved query results.

Question: {state['question']}
SQL Used: {state['sql_query']}
Results: {state['query_result']}

Provide a direct answer followed by a summary breakdown.
"""
        response = llm.invoke([HumanMessage(content=prompt)])
        answer = response.content

    return {"final_answer": answer}
def should_continue(state: AgentState) -> str:
    """Routes to self_correct if error exists and retries < 3; otherwise synthesizes."""
    if state.get("error_message") and state["retry_count"] < 3:
        return "self_correct_sql"
    return "synthesize_answer"

# --- Build the StateGraph ---
workflow = StateGraph(AgentState)

workflow.add_node("generate_sql", generate_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("self_correct_sql", self_correct_sql)
workflow.add_node("synthesize_answer", synthesize_answer)

workflow.set_entry_point("generate_sql")
workflow.add_edge("generate_sql", "execute_sql")

workflow.add_conditional_edges(
    "execute_sql",
    should_continue,
    {
        "self_correct_sql": "self_correct_sql",
        "synthesize_answer": "synthesize_answer"
    }
)

# Loop self-corrected queries back into execution
workflow.add_edge("self_correct_sql", "execute_sql")
workflow.add_edge("synthesize_answer", END)

app = workflow.compile()

if __name__ == "__main__":
    db_schema = get_db_schema()

    sample_questions = [
        "Which customer spent the most money overall, and what country are they from?",
        "What is our top selling product category by total sales volume?"
    ]

    for q in sample_questions:
        print(f"\n==========================================")
        print(f"QUESTION: {q}")
        print(f"==========================================")

        initial_state = {
            "question": q,
            "schema": db_schema,
            "sql_query": None,
            "query_result": None,
            "error_message": None,
            "retry_count": 0,
            "final_answer": None
        }

        # Stream node execution to observe state changes
        for event in app.stream(initial_state):
            for node_name, state_patch in event.items():
                print(f"\n[Node Executed]: {node_name}")
                if "sql_query" in state_patch:
                    print(f"  SQL: {state_patch['sql_query']}")
                if "error_message" in state_patch and state_patch["error_message"]:
                    print(f"  Error: {state_patch['error_message']}")
                if "final_answer" in state_patch:
                    print(f"\n[Answer]:\n{state_patch['final_answer']}")