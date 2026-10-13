from typing import Any, Dict
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.config import settings
from app.agent.state import AgentState, SQLOutput
from app.agent.prompts import SQL_GENERATION_PROMPT, SQL_CORRECTION_PROMPT, SYNTHESIS_PROMPT
from app.database.connection import execute_raw_sql
from app.database.guardrails import validate_sql, SQLSecurityException

# Initialize provider dynamically based on settings
if settings.llm_provider == "gemini":
    base_llm = ChatGoogleGenerativeAI(model=settings.llm_model, temperature=0)
else:
    base_llm = ChatOpenAI(model=settings.llm_model, temperature=0)

structured_sql_llm = base_llm.with_structured_output(SQLOutput)

def generate_sql(state: AgentState) -> Dict[str, Any]:
    prompt = SQL_GENERATION_PROMPT.format(schema=state["schema"], question=state["question"])
    response: SQLOutput = structured_sql_llm.invoke([HumanMessage(content=prompt)])
    return {"sql_query": response.sql_query, "error_message": None}

def execute_sql(state: AgentState) -> Dict[str, Any]:
    query = state["sql_query"]
    try:
        validated_query = validate_sql(query)
    except SQLSecurityException as sec_err:
        return {"query_result": None, "error_message": f"Security Guardrail Triggered: {str(sec_err)}"}

    results, error = execute_raw_sql(validated_query)
    return {"query_result": results, "error_message": error}

def self_correct_sql(state: AgentState) -> Dict[str, Any]:
    prompt = SQL_CORRECTION_PROMPT.format(
        schema=state["schema"],
        question=state["question"],
        sql_query=state["sql_query"],
        error_message=state["error_message"]
    )
    response: SQLOutput = structured_sql_llm.invoke([HumanMessage(content=prompt)])
    return {
        "sql_query": response.sql_query,
        "retry_count": state["retry_count"] + 1,
        "error_message": None
    }

def synthesize_answer(state: AgentState) -> Dict[str, Any]:
    if state.get("error_message"):
        answer = f"Query resolution failed after {state['retry_count']} iterations. Last error: {state['error_message']}"
    else:
        prompt = SYNTHESIS_PROMPT.format(
            question=state["question"],
            sql_query=state["sql_query"],
            query_result=state["query_result"]
        )
        response = base_llm.invoke([HumanMessage(content=prompt)])
        answer = response.content

    return {"final_answer": answer}