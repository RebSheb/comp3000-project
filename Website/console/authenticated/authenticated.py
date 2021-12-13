from flask import render_template, Blueprint

auth_bp = Blueprint("authenticated", __name__)


@auth_bp.route("/home")
def home():
    return render_template("index.jinja2")

@auth_bp.route("/about")
def about():
    return render_template("about.jinja2")