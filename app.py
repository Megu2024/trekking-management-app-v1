from flask import Flask
from flask_login import LoginManager
from database import db

app = Flask(__name__)
app.config["SECRET_KEY"] = "trekking_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/database.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "main.login"

from models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from routes import main
app.register_blueprint(main)
with app.app_context():
    db.create_all()
print(app.url_map)
if __name__ == "__main__":
    app.run(debug=True)

from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(email="admin@trek.com").first()

    if not admin:
        admin = User(
            name="Administrator",
            email="admin@trek.com",
            phone="9391146099",
            role="admin",
            is_approved=True,
            is_blacklisted=False,
            password=generate_password_hash("iitmadmin@trek2026"),
        )
        db.session.add(admin)
        db.session.commit()