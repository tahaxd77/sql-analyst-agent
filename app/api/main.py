from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agent.graph import agent_executor
from app.database.connection import get_db_schema

api = FastAPI(
    title="Self-Correcting SQL Analyst Service",
    version="1.0.0",
    description="Production-grade agentic Text-to-SQL API with AST safety validation and self-reflection loops."
)

class QueryPayload(BaseModel):
    session_id: str
    question: str

@api.get("/health")
def health():
    return {"status": "healthy"}

@api.post("/query")
async def process_question(payload: QueryPayload):
    try:
        config = {"configurable": {"thread_id": payload.session_id}}
        state_input = {
            "question": payload.question,
            "schema": get_db_schema(),
            "sql_query": None,
            "query_result": None,
            "error_message": None,
            "retry_count": 0,
            "final_answer": None
        }
        output = agent_executor.invoke(state_input, config=config)
        return {
            "question": payload.question,
            "sql_query": output["sql_query"],
            "retries_needed": output["retry_count"],
            "error": output["error_message"],
            "result_data": output["query_result"],
            "final_answer": output["final_answer"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))