
from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user
from console import app
from console.models import User


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

        if login_user(user):
            print("Successfully logged in {}".format(user.username))
            return redirect(url_for("authenticated.home"))

    except KeyError as err:
        flash("Please enter login details!")
        return redirect(url_for("login"))


@app.route("/register")
def register():
    return render_template("register.jinja2")
