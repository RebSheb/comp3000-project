from logging import log
from ..app import db, bcrypt
from flask_login import UserMixin
import datetime


class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    registered_on = db.Column(db.DateTime, nullable=False)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password, 12)
        self.registered_on = datetime.datetime.now()

    def __repr__(self):
        return "<User {}>".format(self.username)
