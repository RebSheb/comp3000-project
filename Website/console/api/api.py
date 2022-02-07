from flask import render_template, Blueprint
from flask_login import login_required
from flask_login.utils import logout_user
from werkzeug.utils import redirect

api_bp = Blueprint("api_bp", __name__)

