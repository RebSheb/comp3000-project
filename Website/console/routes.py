
from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user
from console import app, db, bcrypt
from console.models import User


@app.before_first_request
def create_admin_user():
    try:
        default_user_exists = User.query.filter_by(
            name="Built-in Administrator").first()
        if default_user_exists is None:
            print("Initial admin user does not exist, creating...")
            user = User(
                app.config["DEFAULT_USERNAME"], app.config["DEFAULT_USERPASS"], "Built-in Administrator", True)
            db.session.add(user)
            db.session.commit()
            print("Initial admin user created and committed to database...")
        else:
            print("Initial admin user already exists.")

    except Exception as err:
        db.session.rollback()
        print(err)
        print("An unknown error occurred creating default administrator")


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.jinja2")


@app.route("/login", methods=["POST"])
def do_login():
    try:
        user = User.query.filter_by(username=request.form["username"]).first()
        if user is None:
            flash("Please check your username / password!")
            return redirect(url_for("login"))

        if not user.is_active:
            flash(
                "This user is not yet active, please check with your LANMan administrator...")
            return redirect(url_for("login"))

        if not bcrypt.check_password_hash(user.password, request.form["password"]):
            flash("Please check your username / password!")
            return redirect(url_for("login"))

        if login_user(user):
            print("Successfully logged in {}".format(user.username))
            return redirect(url_for("authenticated.home"))

    except KeyError as err:
        flash("Please enter login details!")
        return redirect(url_for("login"))


@app.route("/register", methods=["GET"])
def register():
    return render_template("register.jinja2")


@app.route("/register", methods=["POST"])
def do_register():
    try:
        username = request.form["username"]
        password = request.form["password"]
        name = request.form["name"]
        print("Registering {}:{}".format(username, name))
        user = User(username, password, name)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    except Exception as err:
        print(err)
        db.session.rollback()
        flash("An error occurred whilst trying to register you!")
        return redirect(url_for("register"))
