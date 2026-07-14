# Trekking Management Application

## Project Description

The Trekking Management Application is a Flask-based web application developed as part of the IIT Madras BS Degree Program (MAD-I Project).

The application allows Admin, Trek Staff, and Users (Trekkers) to manage trekking activities through role-based access. It supports trek management, booking management, staff approval, participant tracking, and trekking history.

---

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Jinja2
- Bootstrap 5
- SQLite

---

## Features

### Admin

- Login
- Dashboard with statistics
- Add, edit, and delete treks
- Approve or reject staff registrations
- Assign staff to treks
- View users, staff, and bookings
- Blacklist users or staff

### Trek Staff

- Register and login
- View assigned treks
- Update trek slots
- Update trek status
- View trek participants
- Manage assigned treks

### User

- Register and login
- View available treks
- Search treks
- Book treks
- Cancel bookings
- View booking history
- Update profile

---

## Project Structure

```
trekking-management-app-v1/
│
├── app.py
├── routes.py
├── models.py
├── database.py
├── create_admin.py
├── requirements.txt
│
├── templates/
│   ├── admin/
│   ├── staff/
│   ├── user/
│   ├── base.html
│   ├── login.html
│   └── register.html
│
├── static/
│   └── css/
│
└── instance/
    └── database.sqlite3
```

---

## Installation

Clone the project or extract the project ZIP.

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## Running the Application

Create the default admin account:

```bash
python create_admin.py
```

Start the Flask application:

```bash
python app.py
```

Open your browser and visit:

```
http://127.0.0.1:5000/
```

---

## Default Admin Credentials

Email:

```
iitmadmin@trek.com
```

Password:

```
iitmadmin@trek2026
```

(Change these credentials if you modified `create_admin.py`.)

---

## Database

- Database: SQLite
- Database tables are created automatically using SQLAlchemy when the application starts.
- No manual database creation is required.

---

## Development Notes

### Issues Encountered

- Prevented duplicate trek bookings by checking only active bookings.
- Prevented overbooking by validating available slots before booking.
- Fixed trek status resetting during trek editing.
- Implemented role-based authentication using Flask-Login.
- Added secure password hashing using Werkzeug Security.

---

## Author

**Name:** P N Megarajan (24F3003242)

**Course:** IIT Madras BS Degree Program

**Project:** MAD-I Project

**Application:** Trekking Management Application v1