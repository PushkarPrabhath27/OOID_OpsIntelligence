import sqlite3
conn = sqlite3.connect('ooid_warehouse.db')
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE name='dim_location'")
print(cursor.fetchone()[0])
conn.close()
