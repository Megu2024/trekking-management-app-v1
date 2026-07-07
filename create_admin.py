from werkzeug.security import generate_password_hash

from app import app
from database import db
from models import User


with app.app_context():

    admin = User.query.filter_by(email="admin@trek.com").first()

    if not admin:

        admin = User(
            name="Administrator",
            email="admin@trek.com",
            password=generate_password_hash("admin123"),
            phone="9391146099",
            role="admin",
            is_approved=True,
            is_blacklisted=False
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin Created Successfully!")

    else:
        print("Admin Already Exists!")