# app/agent/graph.py
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    execute_sql,
    generate_sql,
    self_correct_sql,
    synthesize_answer,
)
from app.agent.state import AgentState
from app.config import settings


def should_continue(state: AgentState) -> str:
  if state.get("error_message") and state["retry_count"] < settings.max_retries:
    return "self_correct_sql"
  return "synthesize_answer"


def build_sql_agent():
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
          "synthesize_answer": "synthesize_answer",
      },
  )
  workflow.add_edge("self_correct_sql", "execute_sql")
  workflow.add_edge("synthesize_answer", END)

  # Checkpointer preserves session history by thread_id
  memory = MemorySaver()
  return workflow.compile(checkpointer=memory)


# Exported as agent_executor for both Streamlit and FastAPI
agent_executor = build_sql_agent()