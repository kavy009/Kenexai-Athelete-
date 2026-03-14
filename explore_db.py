import sqlite3

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("=== TABLES ===")
for t in tables:
    print(f"  {t[0]}")

print("\n=== TABLE SCHEMAS ===")
for t in tables:
    table_name = t[0]
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    cols = cursor.fetchall()
    cursor.execute(f"SELECT COUNT(*) FROM '{table_name}'")
    count = cursor.fetchone()[0]
    print(f"\n--- {table_name} ({count} rows) ---")
    for col in cols:
        print(f"  {col[1]} ({col[2]})")

# Sample rows from key tables
print("\n=== SAMPLE DATA ===")
for t in tables[:5]:
    table_name = t[0]
    cursor.execute(f"SELECT * FROM '{table_name}' LIMIT 3")
    rows = cursor.fetchall()
    cursor.execute(f"PRAGMA table_info('{table_name}')")
    cols = [c[1] for c in cursor.fetchall()]
    print(f"\n--- {table_name} ---")
    print(f"  Columns: {cols}")
    for row in rows:
        print(f"  {row}")

conn.close()
