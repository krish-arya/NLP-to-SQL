import sqlite3

# Create a new valid SQLite database file
conn = sqlite3.connect("example.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID INTEGER PRIMARY KEY,
    Name TEXT,
    Email TEXT,
    Phone TEXT,
    Age INTEGER,
    City TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Orders (
    OrderID INTEGER PRIMARY KEY,
    CustomerID INTEGER,
    OrderDate TEXT,
    Amount REAL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
)
""")

# Insert customers
customers = [
    (1, 'Aarav Sharma', 'aarav.sharma@example.com', '9876543210', 28, 'Delhi'),
    (2, 'Isha Verma', 'isha.verma@example.com', '9123456789', 25, 'Mumbai'),
    (3, 'Raj Patel', 'raj.patel@example.com', '9988776655', 32, 'Ahmedabad'),
    (4, 'Simran Kaur', 'simran.kaur@example.com', '9765432109', 30, 'Chandigarh'),
    (5, 'Priya Das', 'priya.das@example.com', '9234567890', 27, 'Kolkata')
]
cursor.executemany("INSERT INTO Customers VALUES (?, ?, ?, ?, ?, ?)", customers)

# Insert orders (12 for Aarav)
orders = []
for i in range(12):
    orders.append((i+1, 1, f"2025-07-{i+1:02d}", 100 + i * 10))  # Orders 1–12 for Aarav

# 3 orders for Isha
orders += [
    (13, 2, "2025-07-03", 150),
    (14, 2, "2025-07-10", 160),
    (15, 2, "2025-07-12", 170)
]

# 9 orders for Raj
for i in range(16, 25):
    orders.append((i, 3, f"2025-07-{i - 15:02d}", 200))

cursor.executemany("INSERT INTO Orders VALUES (?, ?, ?, ?)", orders)

conn.commit()
conn.close()
print("✅ Database created with test data.")
