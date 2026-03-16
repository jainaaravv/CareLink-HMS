# Hospital Management System

A comprehensive, role-based Hospital Management System built to streamline daily operations, patient interactions, and administrative oversight within a healthcare facility. 

## 📌 Project Overview
The system provides a unified platform with distinct portals for **Administrators**, **Doctors**, and **Patients**. It facilitates efficient appointment scheduling, doctor availability management, patient profile tracking, and secure record-keeping. Built with a focus on simplicity, scalability, and robust user experience.

## ✨ Key Features
### Role-Based Access Control
- **Administrator Dashboard:** 
  - Manage user accounts (Doctors, Patients, Departments).
  - Monitor global hospital statistics and appointment trends.
  - Export data (Doctors, Patients, Appointments) to strictly formatted `.csv` files for external analysis.
- **Doctor Portal:**
  - View upcoming appointments and scheduled patients.
  - Update weekly availability slots (Morning, Afternoon, Evening).
  - Record patient diagnosis, prescriptions, and session notes.
  - View individual patient medical histories.
- **Patient Portal:**
  - Browse available doctors by department.
  - Book and track medical appointments.
  - Manage personal profile information and upload profile pictures.

### Core Functionality
- **Dynamic Scheduling:** Prevents double-booking via robust database indexing.
- **Data Export:** Seamless CSV export capabilities for administrators.
- **Modular Data Storage:** Dedicated tables for User Roles, Profiles, Departments, Appointments, and Availability.

## 🛠 Technology Stack
- **Backend:** Python, Flask (Web Framework)
- **Database:** SQLite3 (Lightweight, serverless relational database)
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Standard Libraries:** `csv`, `io`, `os`, `werkzeug.utils` (for secure file uploads), `datetime`

## 📂 Architecture and Structure
The application follows a traditional MVT (Model-View-Template) architecture suited for Flask applications:
- **`app.py`**: The central application logic, routing, role-based authentication, and direct database execution.
- **`schema.sql`**: Defines the normalized relational database structures and constraints, including indexing for unique bounds.
- **`templates/`**: Holds HTML views rendered with Jinja2 for dynamic content.
- **`static/`**: Contains assets like CSS styling, and uploaded user profile pictures (`patient_pfps`, `doctor_pfps`).

## 🚀 Setup & Installation
Follow these steps to run the application locally:

### Prerequisites
- Python 3.8+ installed on your system.

### Installation Steps
1. **Clone the repository** (if applicable) and navigate to the project directory:
   ```bash
   cd hospital-management-system
   ```
2. **Install dependencies**:
   ```bash
   pip install flask werkzeug
   ```
3. **Database Initialization**:
   The `schema.sql` is provided. If `hospital.db` is not present, you can uncomment `init_db()` in `app.py` or manually execute the schema:
   ```bash
   sqlite3 hospital.db < schema.sql
   ```
   *(Note: The `init_db` method also seeds a default `admin` account with username `admin` and password `admin123`)*

4. **Run the Application**:
   ```bash
   python app.py
   ```
   The server will start on `http://127.0.0.1:5000/`.

## 🗄 Database Design
The SQLite database (`hospital.db`) adheres to a normalized operational schema:
- **`users`**: Centralized authentication table storing credentials and roles.
- **`doctors` & `patients`**: Profile metadata mapping 1:1 with the `users` table.
- **`departments`**: Administrative lookup table for specializations.
- **`appointments`**: Transactional table tracking doctor-patient interactions, statuses, and post-session notes.
- **`availabilities`**: Tracking weekly doctor time slots.

## 🛡 Security & Best Practices
- **Idempotent Initialization:** The initial admin seed query contains an `INSERT OR IGNORE` to prevent runtime collisions on reboot.
- **Secure File Handling:** Uses `werkzeug.utils.secure_filename` to sanitize uploaded user files before saving them to the filesystem to prevent path-traversal attacks.
- **Foreign Constraints:** Relies heavily on SQLite foreign keys to maintain data integrity when related records are modified.

---
*Created as a replica of a Hospital Management System.*
