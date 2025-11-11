-- Users table (admin, doctor, patient logins)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'patient'))
);

-- Doctor profiles
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    specialization TEXT NOT NULL,  -- this will hold the department name
    contact TEXT
);


-- Patient profiles
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,  -- links to users.id
    name TEXT NOT NULL,
    contact TEXT
);

-- Departments table (admin manages these, link doctors/patients by department name or id)
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    overview TEXT
);

-- Doctor availability for next 7 days
CREATE TABLE IF NOT EXISTS doctor_availability (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    available_date TEXT NOT NULL,
    available_time TEXT NOT NULL,
    FOREIGN KEY (doctor_id) REFERENCES users(id)
);

-- Appointment record
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('Booked', 'Completed', 'Cancelled')),
    diagnosis TEXT,
    prescription TEXT,
    notes TEXT,
    FOREIGN KEY (doctor_id) REFERENCES users(id),
    FOREIGN KEY (patient_id) REFERENCES users(id)
);

-- Ensure no double-booking for doctor on same date+time
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_appointment
    ON appointments(doctor_id, date, time);
    
CREATE TABLE IF NOT EXISTS availabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER,
    date TEXT,
    slot_morning TEXT,   -- "available" or "unavailable"
    slot_afternoon TEXT,
    slot_evening TEXT,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);
