from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from database import db
from models import User, Trek, Booking, StaffProfile
from datetime import datetime
from sqlalchemy import or_
main = Blueprint("main", __name__)



@main.route("/")
def home():

    if current_user.is_authenticated:

        if current_user.role == "admin":
            return redirect(url_for("main.admin_dashboard"))

        elif current_user.role == "staff":
            return redirect(url_for("main.staff_dashboard"))

        elif current_user.role == "user":
            return redirect(url_for("main.user_dashboard"))

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
        if user.is_blacklisted:
            flash("Your account has been blacklisted by the Admin.")
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

    total_users = User.query.filter_by(role="user").count()

    total_staff = User.query.filter_by(role="staff").count()

    total_treks = Trek.query.count()

    total_bookings = Booking.query.count()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_staff=total_staff,
        total_treks=total_treks,
        total_bookings=total_bookings,
        current_user=current_user
    )


@main.route("/admin/add_trek", methods=["GET", "POST"])
@login_required
def add_trek():

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    if request.method == "POST":

        trek_name = request.form["trek_name"]
        location = request.form["location"]
        difficulty = request.form["difficulty"]
        duration = int(request.form["duration"])
        available_slots = int(request.form["available_slots"])

        status = request.form["status"]

        start_date = datetime.strptime(
            request.form["start_date"],
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            request.form["end_date"],
            "%Y-%m-%d"
        ).date()

        description = request.form["description"]

        assigned_staff_id = request.form["assigned_staff"]

        if assigned_staff_id == "":
            assigned_staff_id = None
        else:
            assigned_staff_id = int(assigned_staff_id)

        trek = Trek(
            trek_name=trek_name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=available_slots,
            status=status,
            start_date=start_date,
            end_date=end_date,
            description=description,
            assigned_staff_id=assigned_staff_id
        )

        db.session.add(trek)
        db.session.commit()

        flash("Trek Added Successfully!")

        return redirect(url_for("main.admin_dashboard"))

    staff = User.query.filter_by(
        role="staff",
        is_approved=True
    ).all()

    return render_template(
        "admin/add_trek.html",
        staff=staff
    )


@main.route("/staff")
@login_required
def staff_dashboard():

    if current_user.role != "staff":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    assigned_treks = Trek.query.filter_by(
        assigned_staff_id=current_user.id
    ).all()

    total_treks = len(assigned_treks)

    total_trekkers = 0

    for trek in assigned_treks:

        total_trekkers += Booking.query.filter_by(
            trek_id=trek.id
        ).count()

    return render_template(

        "staff/dashboard.html",

        assigned_treks=assigned_treks,

        total_treks=total_treks,

        total_trekkers=total_trekkers

    )


@main.route("/staff/profile", methods=["GET", "POST"])
@login_required
def staff_profile():

    if current_user.role != "staff":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]

        # Check if email already belongs to another user
        existing_user = User.query.filter(
            User.email == email,
            User.id != current_user.id
        ).first()

        if existing_user:
            flash("Email already exists!")
            return redirect(url_for("main.staff_profile"))

        current_user.name = name
        current_user.email = email
        current_user.phone = phone

        if password:
            current_user.password = generate_password_hash(password)

        db.session.commit()

        flash("Profile Updated Successfully!")
        return redirect(url_for("main.staff_profile"))

    return render_template("staff/profile.html")

@main.route("/staff/edit_trek/<int:trek_id>", methods=["GET", "POST"])
@login_required
def edit_assigned_trek(trek_id):

    if current_user.role != "staff":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    trek = Trek.query.get_or_404(trek_id)

    # Security Check
    if trek.assigned_staff_id != current_user.id:
        flash("You can only manage your assigned treks.")
        return redirect(url_for("main.staff_dashboard"))

    if request.method == "POST":

        slots = int(request.form["available_slots"])

        if slots < 0:
            flash("Available slots cannot be negative.")
            return redirect(
                url_for(
                    "main.edit_assigned_trek",
                    trek_id=trek.id
                )
            )

        trek.available_slots = slots
        trek.status = request.form["status"]

        db.session.commit()

        flash("Trek Updated Successfully!")

        return redirect(url_for("main.staff_dashboard"))

    return render_template(
        "staff/edit_trek.html",
        trek=trek
    )


@main.route("/staff/participants/<int:trek_id>")
@login_required
def view_participants(trek_id):

    if current_user.role != "staff":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    trek = Trek.query.get_or_404(trek_id)

    # Security check
    if trek.assigned_staff_id != current_user.id:
        flash("You can only view participants of your assigned treks.")
        return redirect(url_for("main.staff_dashboard"))

    bookings = Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    return render_template(
        "staff/participants.html",
        trek=trek,
        bookings=bookings
    )

@main.route("/user")
@login_required
def user_dashboard():

    if current_user.role != "user":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    total_bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).count()

    available_treks = Trek.query.filter(
        Trek.status == "Open",
        Trek.available_slots > 0
    ).count()

    return render_template(
        "user/dashboard.html",
        total_bookings=total_bookings,
        available_treks=available_treks
    )




@main.route("/user/profile", methods=["GET", "POST"])
@login_required
def user_profile():

    if current_user.role != "user":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    if request.method == "POST":

        current_user.name = request.form["name"]
        current_user.email = request.form["email"]
        current_user.phone = request.form["phone"]

        password = request.form["password"]

        if password != "":
            current_user.password = generate_password_hash(password)

        db.session.commit()

        flash("Profile Updated Successfully!")

        return redirect(url_for("main.user_profile"))

    return render_template("user/profile.html")


@main.route("/user/treks")
@login_required
def view_available_treks():

    if current_user.role != "user":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    search = request.args.get("search", "")
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")

    treks = Trek.query.filter(
        Trek.status == "Open",
        Trek.available_slots > 0
    )

    if search:
        treks = treks.filter(
            Trek.trek_name.ilike(f"%{search}%")
        )

    if difficulty:
        treks = treks.filter(
            Trek.difficulty == difficulty
        )

    if location:
        treks = treks.filter(
            Trek.location.ilike(f"%{location}%")
        )

    treks = treks.all()

    return render_template(
        "user/view_treks.html",
        treks=treks,
        search=search,
        difficulty=difficulty,
        location=location
    )


@main.route("/user/book/<int:trek_id>")
@login_required
def book_trek(trek_id):

    if current_user.role != "user":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    trek = Trek.query.get_or_404(trek_id)

    # Trek must be open
    if trek.status != "Open":
        flash("This trek is not open for booking.")
        return redirect(url_for("main.view_available_treks"))

    # Slots available
    if trek.available_slots <= 0:
        flash("Sorry! Trek is already full.")
        return redirect(url_for("main.view_available_treks"))

    # Duplicate booking check
    existing_booking = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id
    ).first()

    if existing_booking:
        flash("You have already booked this trek.")
        return redirect(url_for("main.view_available_treks"))

    booking = Booking(
        user_id=current_user.id,
        trek_id=trek.id,
        status="Booked",
        payment_status="Pending"
    )

    db.session.add(booking)

    trek.available_slots -= 1

    db.session.commit()

    flash("Trek Booked Successfully!")

    return redirect(url_for("main.my_bookings"))

@main.route("/user/bookings")
@login_required
def my_bookings():

    if current_user.role != "user":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "user/my_bookings.html",
        bookings=bookings
    )



@main.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully!")

    return redirect(url_for("main.login"))

@main.route("/admin/treks")
@login_required
def view_treks():

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    search = request.args.get("search", "")

    if search:

        treks = Trek.query.filter(

        or_(

            Trek.trek_name.ilike(f"%{search}%"),

            Trek.id == int(search) if search.isdigit() else False

        )

        ).all()

    else:

        treks = Trek.query.all()

    return render_template(
        "admin/treks.html",
        treks=treks,
        search=search
    )

@main.route("/admin/edit_trek/<int:trek_id>", methods=["GET", "POST"])
@login_required
def edit_trek(trek_id):

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":

        trek.trek_name = request.form["trek_name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration = int(request.form["duration"])
        trek.available_slots = int(request.form["available_slots"])
        trek.status = request.form["status"]

        trek.start_date = datetime.strptime(
            request.form["start_date"],
            "%Y-%m-%d"
        ).date()

        trek.end_date = datetime.strptime(
            request.form["end_date"],
            "%Y-%m-%d"
        ).date()

        trek.description = request.form["description"]
        staff_id = request.form.get("assigned_staff")

        if staff_id:
           trek.assigned_staff_id = int(staff_id)
        else:
           trek.assigned_staff_id = None

        assigned_staff = request.form["assigned_staff"]

        if assigned_staff == "":
            trek.assigned_staff_id = None
        else:
            trek.assigned_staff_id = int(assigned_staff)

        db.session.commit()

        flash("Trek Updated Successfully!")

        return redirect(url_for("main.view_treks"))

    staff = User.query.filter_by(
        role="staff",
        is_approved=True
    ).all()


    staff_members = User.query.filter_by(
    role="staff",
    is_approved=True,
    is_blacklisted=False
).all()
    return render_template(
    "admin/edit_trek.html",
    trek=trek,
    staff_members=staff_members
)

@main.route("/admin/delete_trek/<int:trek_id>")
@login_required
def delete_trek(trek_id):

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)

    db.session.commit()

    flash("Trek Deleted Successfully!")

    return redirect(url_for("main.view_treks"))


@main.route("/admin/staff")
@login_required
def manage_staff():

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    search = request.args.get("search", "")

    if search:

        staff = User.query.filter(

        User.role == "staff",

        or_(

            User.name.ilike(f"%{search}%"),

            User.id == int(search) if search.isdigit() else False

        )

    ).all()

    else:

        staff = User.query.filter_by(role="staff").all()

    return render_template(
        "admin/manage_staff.html",
        staff=staff,
        search=search
    )

@main.route("/admin/approve_staff/<int:user_id>")
@login_required
def approve_staff(user_id):

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    staff = User.query.get_or_404(user_id)

    staff.is_approved = True

    db.session.commit()

    flash("Staff Approved Successfully!")

    return redirect(url_for("main.manage_staff"))

@main.route("/admin/users")
@login_required
def manage_users():

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    search = request.args.get("search", "")

    if search:

        users = User.query.filter(

        User.role == "user",

        or_(

            User.name.ilike(f"%{search}%"),

            User.id == int(search) if search.isdigit() else False

        )

       ).all()

    else:

        users = User.query.filter_by(role="user").all()

    return render_template(
        "admin/manage_users.html",
        users=users,
        search=search
    )


@main.route("/admin/blacklist_user/<int:user_id>")
@login_required
def blacklist_user(user_id):

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    user = User.query.get_or_404(user_id)

    user.is_blacklisted = True

    db.session.commit()

    flash("User Blacklisted Successfully!")

    return redirect(url_for("main.manage_users"))


@main.route("/admin/unblacklist_user/<int:user_id>")
@login_required
def unblacklist_user(user_id):

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    user = User.query.get_or_404(user_id)

    user.is_blacklisted = False

    db.session.commit()

    flash("User Activated Successfully!")

    return redirect(url_for("main.manage_users"))



@main.route("/admin/blacklist_staff/<int:user_id>")
@login_required
def blacklist_staff(user_id):

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    staff = User.query.get_or_404(user_id)

    staff.is_blacklisted = True

    db.session.commit()

    flash("Staff Blacklisted Successfully!")

    return redirect(url_for("main.manage_staff"))

@main.route("/admin/unblacklist_staff/<int:user_id>")
@login_required
def unblacklist_staff(user_id):

    if current_user.role != "admin":
        flash("Access Denied!")
        return redirect(url_for("main.login"))

    staff = User.query.get_or_404(user_id)

    staff.is_blacklisted = False

    db.session.commit()

    flash("Staff Activated Successfully!")

    return redirect(url_for("main.manage_staff"))