# app/agent/state.py
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class IntentClassification(BaseModel):
    is_relevant: bool = Field(
        description="True if the user is asking a data question answerable by the database (orders, customers, sales, products). False if it is chit-chat, programming help, general knowledge, or completely off-topic."
    )
    explanation: str = Field(description="Brief reason for the classification.")

class SQLOutput(BaseModel):
    sql_query: str = Field(description="The executable SQLite query without markdown backticks.")
    reasoning: str = Field(description="Step-by-step logic detailing joins, filters, and aggregations.")

class AgentState(TypedDict):
    question: str
    schema: str
    is_relevant: Optional[bool]        # Added
    sql_query: Optional[str]
    query_result: Optional[List[Dict[str, Any]]]
    error_message: Optional[str]
    retry_count: int
    final_answer: Optional[str]