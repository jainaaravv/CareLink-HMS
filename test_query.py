import sqlite3
conn = sqlite3.connect('hospital.db')


doctors = conn.execute('SELECT * FROM doctors').fetchall()
print("Doctors table:")
print(doctors)


rows = conn.execute('SELECT u.id, u.username, d.specialization, d.contact FROM users u JOIN doctors d ON u.id = d.id WHERE u.role="doctor"').fetchall()
print("Doctors JOIN users table:")
print(rows)
