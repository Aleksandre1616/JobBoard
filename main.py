from flask import Flask, render_template, redirect, url_for, flash, request
from extensions import db, login_manager

import os
import secrets
import requests
import logging
from PIL import Image

app = Flask(__name__)
app.config["SECRET_KEY"] = "jobboard-secret-key-2026"
# SQL Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jobboard.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

logging.basicConfig(
    filename="jobboard.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("JobBoard application started")

db.init_app(app)
login_manager.init_app(app)

from models import User, Job, Category

from forms import RegistrationForm, LoginForm, JobForm, ProfileForm, DeleteForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, file_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + file_ext

    picture_path = os.path.join(
        app.root_path,
        "static",
        "profile_pics",
        picture_filename
    )

    output_size = (150, 150)
    image = Image.open(form_picture)
    image.thumbnail(output_size)
    image.save(picture_path)

    return picture_filename

def get_usd_to_gel():
    try:
        response = requests.get(
            "https://api.frankfurter.dev/v2/rate/usd/gel",
            timeout=5
        )

        response.raise_for_status()

        data = response.json()
        return data["rate"]

    except requests.RequestException as e:
        logging.error(f"API request error: {e}")
        return None

@app.route("/")
def home():
    search = request.args.get("search", "")
    sort = request.args.get("sort", "newest")
    category_id = request.args.get("category", type=int)

    jobs_query = Job.query

    if search:
        jobs_query = jobs_query.filter(
            Job.title.ilike(f"%{search}%")
        )
    if category_id:
        jobs_query = jobs_query.filter_by(category_id=category_id)

    if sort == "oldest":
        jobs_query = jobs_query.order_by(Job.date_posted.asc())
    else:
        jobs_query = jobs_query.order_by(Job.date_posted.desc())

    categories = Category.query.all()
    jobs = jobs_query.all()

    usd_to_gel = get_usd_to_gel()

    return render_template(
        "home.html",
        jobs=jobs,
        search=search,
        sort=sort,
        categories=categories,
        category_id=category_id,
        usd_to_gel=usd_to_gel

    )

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/job/<int:job_id>")
def job_detail(job_id):
    job = db.get_or_404(Job, job_id)
    delete_form = DeleteForm()
    return render_template("job_detail.html", job=job, delete_form=delete_form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            flash("This email is already registered.", "danger")
            return render_template("register.html", form=form)

        hashed_password = generate_password_hash(form.password.data)

        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully!", "success")

        return redirect(url_for("home"))

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            logging.info(f"Successful login: {user.email}")
            flash("Login successful!", "success")
            return redirect(url_for("home"))

        logging.warning(f"Failed login attempt: {form.email.data}")
        flash("Invalid email or password.", "danger")

    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/add-job", methods=["GET", "POST"])
@login_required
def add_job():
    form = JobForm()
    form.category.choices = [
        (category.id, category.name)
        for category in Category.query.all()
    ]
    if form.validate_on_submit():
        job = Job(
            title=form.title.data,
            short_description=form.short_description.data,
            description=form.description.data,
            company=form.company.data,
            salary=form.salary.data,
            location=form.location.data,
            author_id=current_user.id,
            category_id=form.category.data
        )

        db.session.add(job)
        db.session.commit()
        logging.info(f"Job added: {job.title} by {current_user.email}")

        flash("Job added successfully!", "success")
        return redirect(url_for("home"))

    return render_template("add_job.html", form=form)

@app.route("/job/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    job = db.get_or_404(Job, job_id)

    if job.author_id != current_user.id:
        flash("You are not allowed to edit this job.", "danger")
        return redirect(url_for("home"))

    form = JobForm()

    form.category.choices = [
        (category.id, category.name)
        for category in Category.query.all()
    ]

    if form.validate_on_submit():
        job.title = form.title.data
        job.short_description = form.short_description.data
        job.description = form.description.data
        job.company = form.company.data
        job.salary = form.salary.data
        job.location = form.location.data
        job.category_id = form.category.data


        db.session.commit()
        logging.info(f"Job edited: {job.title} by {current_user.email}")

        flash("Job updated successfully!", "success")
        return redirect(url_for("job_detail", job_id=job.id))

    if not form.is_submitted():
        form.title.data = job.title
        form.short_description.data = job.short_description
        form.description.data = job.description
        form.company.data = job.company
        form.salary.data = job.salary
        form.location.data = job.location
        form.category.data = job.category_id

    return render_template("edit_job.html", form=form, job=job)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image = picture_file
            
        current_user.name = form.name.data
        current_user.email = form.email.data

        db.session.commit()

        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    if request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email

    return render_template(
        "profile.html",
        form=form,
        user=current_user
    )
@app.route("/user/<int:user_id>")
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    jobs = Job.query.filter_by(author_id=user.id).order_by(Job.date_posted.desc()).all()

    return render_template(
        "user_profile.html",
        user=user,
        jobs=jobs
    )
@app.route("/job/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id):
    job = db.get_or_404(Job, job_id)

    if job.author_id != current_user.id:
        flash("You are not allowed to delete this job.", "danger")
        return redirect(url_for("home"))

    job_title = job.title
    db.session.delete(job)
    db.session.commit()
    logging.info(f"Job deleted: {job_title} by {current_user.email}")

    flash("Job deleted successfully!", "success")
    return redirect(url_for("home"))

with app.app_context():
    db.create_all()

    if not Category.query.first():
        categories = [
            Category(name="IT"),
            Category(name="Finance"),
            Category(name="Marketing"),
            Category(name="Sales"),
            Category(name="Other")
        ]

        db.session.add_all(categories)
        db.session.commit()

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)