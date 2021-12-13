
from flask_sqlalchemy import SQLAlchemy
from .unauthenticated.unauthenticated import unauth_bp
from .authenticated.authenticated import auth_bp
from flask import Flask, render_template
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
app.register_blueprint(unauth_bp)


# Configure flask-login information
login_manager.blueprint_login_views = {
    "unauth_bp": "/login"
}
login_manager.login_message_category = "danger"



@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
    #return User.query.filter(User.id == int(user_id)).first()


db.init_app(app)
login_manager.init_app(app)


@app.route("/")
@login_required
def index():
    return render_template("index.jinja2")
