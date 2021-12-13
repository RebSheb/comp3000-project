
import flask_login
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect
from .authenticated.authenticated import auth_bp
from flask import Flask, render_template
from flask import request, flash, url_for
from flask_login import LoginManager
from flask_login.utils import login_required
from flask_bcrypt import Bcrypt

# Intial Flask App Creation
app = Flask(__name__)
app.config.from_pyfile("configs/test_config.py")

# Extensions Setup
login_manager = LoginManager()
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Import our DB Models
from .models.users import User

# Load our Blueprints
app.register_blueprint(auth_bp)

# Configure flask-login information
login_manager.login_view = "/login"
login_manager.login_message_category = "danger"

db.create_all(app=app)

db.init_app(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect("/login")


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.jinja2")

@app.route("/login", methods=["POST"])
def do_login():
    print(request.form["username"])
    print(request.form["password"])
    user = User.query.filter_by(username=request.form["username"]).first()

    if user is None:
        flash("Please check your username / password!")
        return redirect(url_for("login"))

    flask_login.login_user(user)
    return ""
    

@app.route("/register")
def register():
    return render_template("register.jinja2")