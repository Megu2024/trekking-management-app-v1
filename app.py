from flask import Flask
from database import db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

import models

@app.route("/")
def home():
    return "Trekking Management Application Running"

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)