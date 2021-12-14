from flask import render_template, Blueprint
from flask_login import login_required
from flask_login.utils import logout_user
from werkzeug.utils import redirect

auth_bp = Blueprint("authenticated", __name__, template_folder="templates")


@auth_bp.route("/")
@login_required
def home():
    return render_template("dashboard.jinja2")

@auth_bp.route("/about")
@login_required
def about():
    return render_template("about.jinja2")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")