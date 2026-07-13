from werkzeug.security import generate_password_hash
from app import app
from models import User
from database import db

with app.app_context():
    admin = User.query.filter_by(email="admin@trek.com").first()
    if not admin:
        admin = User(
            name="Administrator",
            email="admin@trek.com",
            phone="9391146099",
            role="admin",
            is_approved=True,
            is_blacklisted=False
            password=generate_password_hash("admin123"),
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin Created Successfully!")
    else:
        print("Admin Already Exists!")