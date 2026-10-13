# app/agent/graph.py
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, END

from app.agent.nodes import (
    classify_intent,
    handle_irrelevant_query,
    generate_sql,
    execute_sql,
    self_correct_sql,
    synthesize_answer,
)
from app.agent.state import AgentState
from app.config import settings

def route_intent(state: AgentState) -> str:
    """Routes to SQL generator if relevant; otherwise terminates early."""
    if state.get("is_relevant"):
        return "generate_sql"
    return "handle_irrelevant_query"

def should_continue(state: AgentState) -> str:
    if state.get("error_message") and state["retry_count"] < settings.max_retries:
        return "self_correct_sql"
    return "synthesize_answer"

def build_sql_agent():
    workflow = StateGraph(AgentState)

    # Register all nodes
    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("handle_irrelevant_query", handle_irrelevant_query)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("self_correct_sql", self_correct_sql)
    workflow.add_node("synthesize_answer", synthesize_answer)

    # 1. Entry point is now the intent classifier
    workflow.set_entry_point("classify_intent")

    # 2. Conditional edge: valid query vs out-of-scope query
    workflow.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "generate_sql": "generate_sql",
            "handle_irrelevant_query": "handle_irrelevant_query",
        }
    )

    # 3. If irrelevant, terminate immediately
    workflow.add_edge("handle_irrelevant_query", END)

    # 4. Normal SQL workflow
    workflow.add_edge("generate_sql", "execute_sql")
    workflow.add_conditional_edges(
        "execute_sql",
        should_continue,
        {
            "self_correct_sql": "self_correct_sql",
            "synthesize_answer": "synthesize_answer",
        }
    )
    workflow.add_edge("self_correct_sql", "execute_sql")
    workflow.add_edge("synthesize_answer", END)

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

agent_executor = build_sql_agent()