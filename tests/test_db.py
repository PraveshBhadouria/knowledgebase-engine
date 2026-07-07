# tests/test_db.py

from database.connection import get_connection

conn = get_connection()

print("DB Connected")

conn.close()