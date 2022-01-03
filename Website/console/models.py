from console import db, bcrypt
from sqlalchemy import DateTime
from flask_login import UserMixin
import datetime


class Device(db.Model):

    mac_address = db.Column(db.Integer, primary_key=True)
    ipv4_address = db.Column(db.String(15), nullable=False)
    last_seen = db.Column(DateTime, nullable=False,
                          default=datetime.datetime.utcnow)
    first_seen = db.Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    updated_at = db.Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, mac_address, ipv4_address) -> None:
        self.mac_address = mac_address
        self.ip_address = ipv4_address
        return

    def __repr__(self):
        return "<Device %r" % self.mac_address


class User(UserMixin, db.Model):

    __tablename__ = "users"

    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
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
