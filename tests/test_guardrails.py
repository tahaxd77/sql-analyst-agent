import pytest
from app.database.guardrails import validate_sql, SQLSecurityException

def test_allows_valid_select():
    sql = "SELECT full_name, email FROM customers WHERE country = 'US';"
    assert "SELECT" in validate_sql(sql).upper()

def test_blocks_drop_table():
    with pytest.raises(SQLSecurityException):
        validate_sql("DROP TABLE customers;")

def test_blocks_delete_injection():
    with pytest.raises(SQLSecurityException):
        validate_sql("DELETE FROM orders WHERE order_id = 1;")

def test_blocks_stacked_mutations():
    with pytest.raises(SQLSecurityException):
        validate_sql("SELECT * FROM customers; DROP TABLE orders;")