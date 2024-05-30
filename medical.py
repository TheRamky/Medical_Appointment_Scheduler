import tkinter as tk
from tkinter import messagebox
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

DATABASE = 'medical_appointments.db'

def setup_database():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('DROP TABLE IF EXISTS patients')
        conn.execute('DROP TABLE IF EXISTS appointments')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dob TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                doctor TEXT NOT NULL,
                reminder_sent INTEGER DEFAULT 0,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        ''')

setup_database()

def add_patient(name, dob, phone, email):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('INSERT INTO patients (name, dob, phone, email) VALUES (?, ?, ?, ?)', 
                     (name, dob, phone, email))

def schedule_appointment(patient_id, appointment_date, doctor):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('INSERT INTO appointments (patient_id, appointment_date, doctor) VALUES (?, ?, ?)', 
                     (patient_id, appointment_date, doctor))

def send_email_reminder(name, email, appointment_date, doctor):
    try:
        msg = MIMEMultipart()
        msg['From'] = 'your_email@example.com'
        msg['To'] = email
        msg['Subject'] = 'Appointment Reminder'
        body = f"Dear {name},\n\nThis is a reminder for your appointment with Dr. {doctor} on {appointment_date}.\n\nThank you."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login('your_email@example.com', 'your_password')
        text = msg.as_string()
        server.sendmail('your_email@example.com', email, text)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_reminders():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.execute('SELECT a.id, p.name, p.phone, p.email, a.appointment_date, a.doctor FROM appointments a JOIN patients p ON a.patient_id = p.id WHERE a.reminder_sent = 0')
        reminders_sent = 0
        for row in cur:
            appointment_id, name, phone, email, appointment_date, doctor = row
            send_email_reminder(name, email, appointment_date, doctor)
            conn.execute('UPDATE appointments SET reminder_sent = 1 WHERE id = ?', (appointment_id,))
            reminders_sent += 1

def view_patients():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.execute('SELECT id, name, dob, phone, email FROM patients')
        patients = cur.fetchall()
        return patients

def view_appointments():
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.execute('SELECT a.id, p.name, a.appointment_date, a.doctor FROM appointments a JOIN patients p ON a.patient_id = p.id')
        appointments = cur.fetchall()
        return appointments

def add_patient_gui():
    add_patient(patient_name.get(), patient_dob.get(), patient_phone.get(), patient_email.get())
    messagebox.showinfo("Info", "Patient record added successfully")

def schedule_appointment_gui():
    schedule_appointment(appointment_patient_id.get(), appointment_date.get(), appointment_doctor.get())
    messagebox.showinfo("Info", "Appointment scheduled successfully")

def send_reminders_gui():
    send_reminders()
    messagebox.showinfo("Info", "Reminders sent successfully")

def view_patients_gui():
    patients = view_patients()
    display_text = "Patient Records:\n"
    for patient in patients:
        display_text += f"ID: {patient[0]}, Name: {patient[1]}, DOB: {patient[2]}, Phone: {patient[3]}, Email: {patient[4]}\n"
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, display_text)

def view_appointments_gui():
    appointments = view_appointments()
    display_text = "Appointments:\n"
    for appointment in appointments:
        display_text += f"ID: {appointment[0]}, Patient: {appointment[1]}, Date: {appointment[2]}, Doctor: {appointment[3]}\n"
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, display_text)

app = tk.Tk()
app.title("Medical Appointment Scheduler")

tk.Label(app, text="Patient Name:").grid(row=0, column=0)
patient_name = tk.Entry(app)
patient_name.grid(row=0, column=1)

tk.Label(app, text="DOB (YYYY-MM-DD):").grid(row=1, column=0)
patient_dob = tk.Entry(app)
patient_dob.grid(row=1, column=1)

tk.Label(app, text="Phone:").grid(row=2, column=0)
patient_phone = tk.Entry(app)
patient_phone.grid(row=2, column=1)

tk.Label(app, text="Email:").grid(row=3, column=0)
patient_email = tk.Entry(app)
patient_email.grid(row=3, column=1)

add_patient_button = tk.Button(app, text="Add Patient", command=add_patient_gui)
add_patient_button.grid(row=4, column=0, columnspan=2)

tk.Label(app, text="Patient ID:").grid(row=5, column=0)
appointment_patient_id = tk.Entry(app)
appointment_patient_id.grid(row=5, column=1)

tk.Label(app, text="Appointment Date (YYYY-MM-DD):").grid(row=6, column=0)
appointment_date = tk.Entry(app)
appointment_date.grid(row=6, column=1)

tk.Label(app, text="Doctor:").grid(row=7, column=0)
appointment_doctor = tk.Entry(app)
appointment_doctor.grid(row=7, column=1)

schedule_appointment_button = tk.Button(app, text="Schedule Appointment", command=schedule_appointment_gui)
schedule_appointment_button.grid(row=8, column=0, columnspan=2)

send_reminders_button = tk.Button(app, text="Send Reminders", command=send_reminders_gui)
send_reminders_button.grid(row=9, column=0, columnspan=2)

view_patients_button = tk.Button(app, text="View Patients", command=view_patients_gui)
view_patients_button.grid(row=10, column=0, columnspan=2)

view_appointments_button = tk.Button(app, text="View Appointments", command=view_appointments_gui)
view_appointments_button.grid(row=11, column=0, columnspan=2)

text_area = tk.Text(app, width=50, height=15)
text_area.grid(row=12, column=0, columnspan=2, pady=10)

app.mainloop()
