# update_passwords.py
import mysql.connector
import hashlib

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='12345678',  # Your MySQL password
    database='demo1'
)

cursor = conn.cursor()

# Generate MD5 hash for '1234'
password_hash = hashlib.md5('1234'.encode()).hexdigest()
print(f"MD5 of '1234' is: {password_hash}")

# Update employee password
cursor.execute("UPDATE users SET password = %s WHERE employee_id = 'EMP001'", (password_hash,))

# Update admin password
admin_hash = hashlib.md5('admin123'.encode()).hexdigest()
cursor.execute("UPDATE users SET password = %s WHERE employee_id = 'EMP006'", (admin_hash,))

# Or update all employees
cursor.execute("UPDATE users SET password = %s WHERE role = 'employee'", (password_hash,))

conn.commit()
print(f"Updated {cursor.rowcount} users")

# Verify
cursor.execute("SELECT employee_id, name, password FROM users")
for row in cursor.fetchall():
    print(f"{row[0]} - {row[1]} - {row[2]}")

cursor.close()
conn.close()