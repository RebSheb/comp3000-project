# __init__.py

from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .authenticated.authenticated import auth_bp
from .api.api import api_bp

app = Flask(__name__)
app.config.from_pyfile("../test_config.py")
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def create_app():
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # Configure flask-login information
    login_manager.login_view = "/login"
    login_manager.login_message_category = "danger"

    login_manager.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    from console import routes, models

    db.create_all(app=app)
    db.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        return redirect("/login")

    @app.before_first_request
    def create_test_user():
        try:
            user = models.User("testtest", "cheese")
            db.session.add(user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            return

    return app
