from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

class SQLOutput(BaseModel):
    sql_query: str = Field(description="The executable SQLite query without markdown backticks.")
    reasoning: str = Field(description="Step-by-step logic detailing joins, filters, and aggregations.")

class AgentState(TypedDict):
    question: str
    schema: str
    sql_query: Optional[str]
    query_result: Optional[List[Dict[str, Any]]]
    error_message: Optional[str]
    retry_count: int
    final_answer: Optional[str]