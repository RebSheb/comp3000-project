from flask import render_template, Blueprint
from flask_login import login_required

auth_bp = Blueprint("authenticated", __name__)


@auth_bp.route("/")
@login_required
def home():
    return render_template("index.jinja2")

@auth_bp.route("/about")
@login_required
def about():
    return render_template("about.jinja2")