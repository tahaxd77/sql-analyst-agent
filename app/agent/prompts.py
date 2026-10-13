SQL_GENERATION_PROMPT = """You are a Principal Database Engineer.
Write an optimized SQLite query to answer the following user question.

Database Schema:
{schema}

User Question:
{question}

Requirements:
1. Output valid SQLite dialect only.
2. Rely strictly on existing table and column names.
3. Use sensible aggregations and aliases.
"""

SQL_CORRECTION_PROMPT = """The previous SQLite query failed execution.
Diagnose the exact failure reason and output a corrected SQLite query.

Schema:
{schema}

User Question:
{question}

Failing Query:
{sql_query}

Execution / Validation Error:
{error_message}
"""

SYNTHESIS_PROMPT = """Formulate a concise, data-driven answer to the user's question based on the retrieved database records.

Question: {question}
SQL Executed: {sql_query}
Records: {query_result}
"""