from flask import render_template, Blueprint

unauth_bp = Blueprint("unauthenticated", __name__)


@unauth_bp.route("/")
def home():
    return render_template("index")

@unauth_bp.route("/login")
def login():
    return render_template("login")

@unauth_bp.route("/register")
def register():
    return render_template("register")