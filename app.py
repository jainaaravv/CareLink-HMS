from flask import Flask, render_template, g, flash, request, redirect, url_for, session, jsonify
import sqlite3
from datetime import date
from flask import Response
import csv
import io
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)  # <-- Only do this ONCE!

UPLOAD_FOLDER = 'static/patient_pfps'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'jaaravv2006'
DATABASE = 'hospital.db'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        # Seed admin account (idempotent)
        db.execute('INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin123', 'admin'))
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin')
def admin_dashboard():
    db = get_db()
    doctor_count = db.execute('SELECT COUNT(*) FROM users WHERE role="doctor"').fetchone()[0]
    patient_count = db.execute('SELECT COUNT(*) FROM users WHERE role="patient"').fetchone()[0]
    appt_count = db.execute('SELECT COUNT(*) FROM appointments').fetchone()[0]
    departments = db.execute('SELECT id, name, overview FROM departments').fetchall()


    doctors = db.execute(
    'SELECT u.id, u.username, d.specialization, d.contact FROM users u '
    'JOIN doctors d ON u.id = d.id WHERE u.role="doctor"').fetchall()
    print(doctors)  # <--- Add this

    upcoming_appointments = db.execute(
    '''
    SELECT a.id, d.username AS doctor_name, p.username AS patient_name, a.date, a.time, a.status
    FROM appointments a
    JOIN users d ON a.doctor_id = d.id
    JOIN users p ON a.patient_id = p.id
    WHERE a.date >= ?
    ORDER BY a.date ASC, a.time ASC
    LIMIT 3
    ''',
    (date.today().isoformat(),)
).fetchall()

    patients = db.execute(
        'SELECT u.id, u.username, p.contact FROM users u '
        'JOIN patients p ON u.id = p.id WHERE u.role="patient"'
    ).fetchall()

    appointments = db.execute(
    '''
    SELECT a.id, d.username AS doctor_name, p.username AS patient_name, a.date, a.time, a.status
    FROM appointments a
    JOIN users d ON a.doctor_id = d.id
    JOIN users p ON a.patient_id = p.id
    ORDER BY a.date DESC, a.time DESC
    '''
).fetchall()
    departments = db.execute('SELECT id, name, overview FROM departments').fetchall()


    return render_template('admin_dashboard.html',
                      doctors=doctors,
                      patients=patients,
                      doctor_count=doctor_count,
                      patient_count=patient_count,
                      appt_count=appt_count,
                      appointments=appointments,
                      upcoming_appointments=upcoming_appointments,departments=departments)



    patients = db.execute(
    'SELECT u.id, u.username, p.contact FROM users u '
    'JOIN patients p ON u.id = p.id WHERE u.role="patient"'
).fetchall()

    appointments = db.execute('SELECT id, doctor_id, patient_id, date, time, status FROM appointments ORDER BY date DESC, time DESC').fetchall()
    return render_template('admin_dashboard.html', doctors=doctors, patients=patients,
                           doctor_count=doctor_count, patient_count=patient_count, appt_count=appt_count,
                           appointments=appointments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
        if user:
            session['user_id'] = user[0]
            session['role'] = user[3]
            if user[3] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user[3] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
        else:
            return "Invalid username or password"
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        contact = request.form.get('contact', '')  # Will be blank for non-patients

        db = get_db()
        try:
            # Insert into users table (all roles)
            db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', 
                        (username, password, role))
            db.commit()
            user = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()

            # If this user is a patient, link a `patients` row as well:
            if role == 'patient':
                db.execute('INSERT INTO patients (id, name, contact) VALUES (?, ?, ?)', 
                           (user[0], username, contact))
                db.commit()
        except sqlite3.IntegrityError:
            flash('Username already exists', 'danger')
            return render_template('register.html')
        flash('Registration successful, please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/doctor')
def doctor_dashboard():
    appointments = [
        {'patient_name': 'John Doe', 'date': '2025-10-20', 'time': '10:00AM'},
        {'patient_name': 'Jane Smith', 'date': '2025-10-21', 'time': '11:00AM'}
    ]
    patients = [
        {'name': 'John Doe'},
        {'name': 'Jane Smith'}
    ]
    return render_template('doctor_dashboard.html', appointments=appointments, patients=patients)



@app.route('/add_doctor', methods=['POST'])
def add_doctor():
    username = request.form['username']
    password = request.form['password']
    specialization = request.form['specialization']
    contact = request.form['contact']
    db = get_db()
    try:
        db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, 'doctor'))
        user_id = db.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()[0]
        db.execute('INSERT INTO doctors (id, name, specialization, contact) VALUES (?, ?, ?, ?)', (user_id, username, specialization, contact))
        db.commit()
        return redirect(url_for('admin_dashboard'))
    except sqlite3.IntegrityError:
        return "Doctor with that username already exists!"

@app.route('/add_patient', methods=['POST'])
def add_patient():
    username = request.form['username']
    password = request.form['password']
    contact = request.form['contact']
    db = get_db()
    try:
        db.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', (username, password, 'patient'))
        user_id = db.execute('SELECT id FROM users WHERE username=?', (username,)).fetchone()[0]
        db.execute('INSERT INTO patients (id, name, contact) VALUES (?, ?, ?)', (user_id, username, contact))
        db.commit()
        return redirect(url_for('admin_dashboard'))
    except sqlite3.IntegrityError:
        return "Patient with that username already exists!"
    
@app.route('/api/doctors/<int:dept_id>')
def api_get_doctors(dept_id):
    db = get_db()
    doctors = db.execute(
        'SELECT d.id, u.username FROM doctors d JOIN users u ON d.id = u.id WHERE d.specialization = (SELECT name FROM departments WHERE id = ?)', (dept_id,)
    ).fetchall()
    return jsonify([{'id': doc[0], 'name': doc[1]} for doc in doctors])

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect(url_for('login'))
    db = get_db()
    user_id = session['user_id']

    patient = db.execute('SELECT name, contact, age, pfp FROM patients WHERE id=?', (user_id,)).fetchone()

    if request.method == "POST":
        new_name = request.form['name']
        new_contact = request.form['contact']
        new_age = request.form['age']
        filename = patient[3]  # default to current pfp
        # Handle profile picture upload
        if 'pfp' in request.files:
            file = request.files['pfp']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{user_id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        db.execute('UPDATE users SET username=? WHERE id=?', (new_name, user_id))
        db.execute('UPDATE patients SET name=?, contact=?, age=?, pfp=? WHERE id=?',
                   (new_name, new_contact, new_age, filename, user_id))
        db.commit()
        flash("Profile updated!", "success")
        return redirect(url_for('patient_dashboard'))

    return render_template("edit_profile.html", patient=patient)



@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    doctor_id = request.form['doctor_id']
    patient_id = request.form['patient_id']
    date = request.form['date']
    time = request.form['time']
    db = get_db()
    try:
        db.execute(
            'INSERT INTO appointments (doctor_id, patient_id, date, time, status) VALUES (?, ?, ?, ?, ?)',
            (doctor_id, patient_id, date, time, 'Booked')
        )
        db.commit()
        flash('Appointment booked!', 'success')
    except sqlite3.IntegrityError:
        flash('This slot is already booked for this doctor. Please choose another time.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_doctor/<int:doctor_id>', methods=['POST'])
def edit_doctor(doctor_id):
    username = request.form['username']
    specialization = request.form['specialization']
    contact = request.form['contact']
    db = get_db()
    # Check for another doctor with this username
    exists = db.execute(
        'SELECT id FROM users WHERE username = ? AND id != ? AND role = "doctor"',
        (username, doctor_id)
    ).fetchone()
    if exists:
        flash('A doctor with that username already exists.', 'danger')
        return redirect(url_for('admin_dashboard'))
    try:
        db.execute('UPDATE users SET username=? WHERE id=? AND role="doctor"', (username, doctor_id))
        db.execute('UPDATE doctors SET name=?, specialization=?, contact=? WHERE id=?', (username, specialization, contact, doctor_id))
        db.commit()
        flash('Doctor updated!', 'success')
    except sqlite3.IntegrityError:
        flash('Username conflict on doctor update.', 'danger')
    return redirect(url_for('admin_dashboard'))


@app.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    db = get_db()
    db.execute('DELETE FROM doctors WHERE id=?', (doctor_id,))
    db.execute('DELETE FROM users WHERE id=? AND role="doctor"', (doctor_id,))
    db.commit()
    flash('Doctor deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_patient/<int:patient_id>', methods=['POST'])
def edit_patient(patient_id):
    username = request.form['username']
    contact = request.form['contact']
    db = get_db()
    # Check for another patient with this username
    exists = db.execute(
        'SELECT id FROM users WHERE username = ? AND id != ? AND role = "patient"',
        (username, patient_id)
    ).fetchone()
    if exists:
        flash('A patient with that username already exists.', 'danger')
        return redirect(url_for('admin_dashboard'))
    try:
        db.execute('UPDATE users SET username=? WHERE id=? AND role="patient"', (username, patient_id))
        db.execute('UPDATE patients SET name=?, contact=? WHERE id=?', (username, contact, patient_id))
        db.commit()
        flash('Patient updated!', 'success')
    except sqlite3.IntegrityError:
        flash('Username conflict on patient update.', 'danger')
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    db = get_db()
    db.execute('DELETE FROM patients WHERE id=?', (patient_id,))
    db.execute('DELETE FROM users WHERE id=? AND role="patient"', (patient_id,))
    db.commit()
    flash('Patient deleted!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/export/patients')
def export_patients():
    db = get_db()
    patients = db.execute(
        'SELECT u.id, u.username, p.contact FROM users u JOIN patients p ON u.id = p.id WHERE u.role="patient"'
    ).fetchall()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Username', 'Contact'])
    cw.writerows(patients)
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=patients.csv"})

@app.route('/export/doctors')
def export_doctors():
    db = get_db()
    doctors = db.execute(
        'SELECT u.id, u.username, d.specialization, d.contact FROM users u JOIN doctors d ON u.id = d.id WHERE u.role="doctor"'
    ).fetchall()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Username', 'Specialization', 'Contact'])
    cw.writerows(doctors)
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=doctors.csv"})

@app.route('/add_department', methods=['POST'])
def add_department():
    dept_name = request.form['dept_name']
    overview = request.form.get('overview', '')
    db = get_db()
    try:
        db.execute('INSERT INTO departments (name, overview) VALUES (?, ?)', (dept_name, overview))
        db.commit()
        flash('Department added!', 'success')
    except sqlite3.IntegrityError:
        flash('Department with that name already exists!', 'danger')
    return redirect(url_for('admin_dashboard'))



@app.route('/patient')
def patient_dashboard():
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect(url_for('login'))

    user_id = session['user_id']
    db = get_db()

    # Get patient info
    user = db.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        return "User not found!", 404
    patient_name = user[0]

    # Fetch all required fields at once
    patient = db.execute('SELECT contact, age, pfp FROM patients WHERE id = ?', (user_id,)).fetchone()
    patient_contact = patient[0] if patient else ''
    patient_age = patient[1] if patient else ''
    patient_pfp = patient[2] if patient else None

    departments = db.execute('SELECT id, name FROM departments').fetchall()
    appointments = db.execute(
        '''
        SELECT a.id, u.username, a.date, a.time, a.status
        FROM appointments a
          JOIN users u ON a.doctor_id = u.id
        WHERE a.patient_id = ?
        ORDER BY a.date, a.time
        ''',
        (user_id,)
    ).fetchall()

    return render_template(
        'patient_dashboard.html',
        patient_name=patient_name,
        patient_contact=patient_contact,
        patient_age=patient_age,
        patient_pfp=patient_pfp,
        departments=departments,
        upcoming_appointments=appointments
    )


@app.route('/export/appointments')
def export_appointments():
    db = get_db()
    appointments = db.execute(
        '''
        SELECT a.id, d.username AS doctor_name, p.username AS patient_name, a.date, a.time, a.status
        FROM appointments a
        JOIN users d ON a.doctor_id = d.id
        JOIN users p ON a.patient_id = p.id
        '''
    ).fetchall()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Doctor Name', 'Patient Name', 'Date', 'Time', 'Status'])
    cw.writerows(appointments)
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=appointments.csv"})




if __name__ == '__main__':
     #init_db()   # UNCOMMENT and run ONCE if you ever need to recreate tables!
     app.run(debug=True)
