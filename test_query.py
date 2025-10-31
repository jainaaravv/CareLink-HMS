import sqlite3
conn = sqlite3.connect('hospital.db')

# See all columns and data in doctors table
doctors = conn.execute('SELECT * FROM doctors').fetchall()
print("Doctors table:")
print(doctors)

# Run your joined query as used in your app
rows = conn.execute('SELECT u.id, u.username, d.specialization, d.contact FROM users u JOIN doctors d ON u.id = d.id WHERE u.role="doctor"').fetchall()
print("Doctors JOIN users table:")
print(rows)
