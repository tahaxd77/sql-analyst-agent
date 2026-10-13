# db_setup.py
import sqlite3

def init_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()

    cursor.executescript("""
    DROP TABLE IF EXISTS orders;
    DROP TABLE IF EXISTS customers;
    DROP TABLE IF EXISTS products;

    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        full_name TEXT NOT NULL,
        email TEXT UNIQUE,
        country TEXT NOT NULL,
        signup_date DATE NOT NULL
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER REFERENCES customers(customer_id),
        product_id INTEGER REFERENCES products(product_id),
        quantity INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        order_date DATE NOT NULL
    );

    INSERT INTO customers VALUES 
        (1, 'Alice Smith', 'alice@example.com', 'US', '2025-01-15'),
        (2, 'Bob Jones', 'bob@example.com', 'UK', '2025-02-10'),
        (3, 'Charlie Brown', 'charlie@example.com', 'US', '2025-03-05');

    INSERT INTO products VALUES
        (101, 'Mechanical Keyboard', 'Electronics', 120.0),
        (102, 'Ergonomic Mouse', 'Electronics', 60.0),
        (103, 'Desk Mat', 'Accessories', 25.0);

    INSERT INTO orders VALUES
        (1001, 1, 101, 1, 120.0, '2026-01-10'),
        (1002, 1, 103, 2, 50.0, '2026-02-14'),
        (1003, 2, 102, 1, 60.0, '2026-03-01'),
        (1004, 3, 101, 2, 240.0, '2026-03-12');
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully as store.db")

if __name__ == "__main__":
    init_db()