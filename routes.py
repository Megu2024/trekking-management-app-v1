from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from database import db
from models import User

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return redirect(url_for("main.login"))


@main.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        phone = request.form["phone"]
        role = request.form["role"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered!")
            return redirect(url_for("main.register"))

        hashed_password = generate_password_hash(password)

        if role == "staff":
            approval = False
        else:
            approval = True

        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            phone=phone,
            role=role,
            is_approved=approval
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful! Please Login.")

        return redirect(url_for("main.login"))

    return render_template("register.html")



@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user is None:
            flash("User does not exist!")
            return redirect(url_for("main.login"))

        if not check_password_hash(user.password, password):
            flash("Incorrect Password!")
            return redirect(url_for("main.login"))

        if user.role == "staff" and not user.is_approved:
            flash("Your account is waiting for Admin approval.")
            return redirect(url_for("main.login"))

        login_user(user)

        if user.role == "admin":
            return redirect(url_for("main.admin_dashboard"))

        elif user.role == "staff":
            return redirect(url_for("main.staff_dashboard"))

        else:
            return redirect(url_for("main.user_dashboard"))

    return render_template("login.html")

@main.route("/admin")
@login_required
def admin_dashboard():

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    return "<h1>Admin Dashboard</h1>"


@main.route("/staff")
@login_required
def staff_dashboard():

    if current_user.role != "staff":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    return "<h1>Staff Dashboard</h1>"


@main.route("/user")
@login_required
def user_dashboard():

    if current_user.role != "user":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    return "<h1>User Dashboard</h1>"

@main.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully!")

    return redirect(url_for("main.login"))