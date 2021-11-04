from flask import render_template, Blueprint

auth_bp = Blueprint("authenticated", __name__)


@auth_bp.route("/console")
def home():
    return render_template("index")
