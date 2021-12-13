from flask import render_template, Blueprint
from flask import current_app as app

unauth_bp = Blueprint("unauthenticated", __name__, template_folder="templates")


@unauth_bp.route("/")
def home():
    return render_template("index.jinja2")

@unauth_bp.route("/logins")
def login():
    return render_template("login.jinja2")

@unauth_bp.route("/register")
def register():
    return render_template("register.jinja2")