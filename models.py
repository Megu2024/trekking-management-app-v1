from flask_login import UserMixin
from database import db
from datetime import datetime

class User(UserMixin,db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    bookings = db.relationship(
        "Booking",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )
    assigned_treks = db.relationship(
        "Trek",
        backref="assigned_staff",
        lazy=True
    )

class Trek(db.Model):
    __tablename__ = "treks"
    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    assigned_staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )
    status = db.Column(
        db.String(20),
        default="Pending"
    )
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    description = db.Column(db.Text)
    bookings = db.relationship(
        "Booking",
        backref="trek",
        lazy=True,
        cascade="all, delete-orphan"
    )

class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id"),
        nullable=False
    )
    booking_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    status = db.Column(
        db.String(20),
        default="Booked"
    )
    payment_status = db.Column(
        db.String(20),
        default="Pending"
    )

