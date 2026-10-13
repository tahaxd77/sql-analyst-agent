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
# app/agent/prompts.py (Add to existing prompts)

INTENT_CLASSIFICATION_PROMPT = """You are a domain classifier for an internal business analytics database.

The database contains tables and records related strictly to:
- Customers (accounts, signup dates, country)
- Products (pricing, categories, catalog)
- Orders (quantities, order dates, totals, revenue)

Database Schema summary:
{schema}

User Input: "{question}"

Evaluate whether this input is a business/data query related to the database records above.
Mark `is_relevant` as False if the input is:
- General conversational filler (e.g., "hi", "how are you?")
- Requests about writing code, marketing copy, or GitHub descriptions (e.g., "give me a description for github")
- Questions unrelated to the business entities in this database.
"""