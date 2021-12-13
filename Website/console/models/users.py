from logging import log
from ..app import db, bcrypt
from flask_login import UserMixin
import datetime


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.generate_password_hash(password, 24)
        self.registered_on = datetime.datetime.now()

    def __repr__(self):
        return "<User {}>".format(self.username)
