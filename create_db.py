import sqlite3

conn = sqlite3.connect('ecommerce.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    country TEXT NOT NULL,
    join_date DATE NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    total_amount REAL,
    status TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
)
''')

print("Tables created successfully!")

customers = [
    (1, 'Rajesh Kumar', 'rajesh@email.com', 'India', '2024-01-15'),
    (2, 'Priya Singh', 'priya@email.com', 'India', '2024-02-20'),
    (3, 'John Smith', 'john@email.com', 'USA', '2024-03-10'),
    (4, 'Emma Wilson', 'emma@email.com', 'UK', '2024-04-05'),
    (5, 'Ahmed Ali', 'ahmed@email.com', 'UAE', '2024-05-12'),    
]
cursor.executemany('INSERT OR IGNORE INTO customers VALUES (?, ?, ?, ?, ?)', customers)

orders = [
    (1, 1, '2025-01-10', 5000.00, 'completed'),
    (2, 1, '2025-02-15', 3000.00, 'completed'),
    (3, 2, '2025-01-20', 7500.00, 'completed'),
    (4, 3, '2025-03-01', 2000.00, 'pending'),
    (5, 2, '2025-03-15', 4500.00, 'completed'),
    (6, 4, '2025-04-10', 6000.00, 'completed'),
    (7, 5, '2025-05-05', 8000.00, 'completed'),
    (8, 1, '2025-06-01', 2500.00, 'completed'),
]
cursor.executemany('INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?, ?)', orders)

products = [
    (1, 'Laptop', 'Electronics', 50000.00, 15),
    (2, 'Phone', 'Electronics', 30000.00, 5),
    (3, 'Headphones', 'Electronics', 5000.00, 50),
    (4, 'Desk Chair', 'Furniture', 8000.00, 8),
    (5, 'Monitor', 'Electronics', 20000.00, 12),
]
cursor.executemany('INSERT OR IGNORE INTO products VALUES (?,?,?,?,?)', products)

print("Sample data inserted successfully!")

conn.commit()
conn.close()
