from flask import render_template, Blueprint, request
from flask_login import login_required
from flask_login.utils import logout_user
from werkzeug.utils import redirect
from console import app, db

api_bp = Blueprint("api_bp", __name__)

@app.route("/agent/post_data", methods=["POST"])
def do_post_data():
    print(request.json)
    return '', 200