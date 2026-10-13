# app/database/guardrails.py
import sqlglot
from sqlglot import exp


class SQLSecurityException(Exception):
    """Raised when an unsafe or non-SELECT query is generated."""

    pass


def validate_sql(sql: str, dialect: str = "sqlite") -> str:
    """Validates that the SQL contains exclusively SELECT queries and transpiles it."""
    try:
        parsed = sqlglot.parse_one(sql, read=dialect)
    except sqlglot.errors.ParseError as err:
        raise SQLSecurityException(f"Syntax validation failed: {str(err)}")

    if not isinstance(parsed, exp.Select):
        raise SQLSecurityException(
            f"Forbidden query statement '{type(parsed).__name__}'. Only read operations (SELECT) are authorized."
        )

    for expression in parsed.walk():
        if isinstance(
            expression,
            (exp.Drop, exp.Delete, exp.Insert, exp.Update, exp.Command),
        ):
            raise SQLSecurityException(
                "Destructive DDL/DML clauses detected."
            )

    return parsed.sql(dialect=dialect)