from console import db, bcrypt
from sqlalchemy import DateTime, desc
from flask_login import UserMixin
import datetime


class Device(db.Model):

    __tablename__ = "devices"
    mac_address = db.Column(db.String(17), primary_key=True)
    ipv4_address = db.Column(db.String(15), nullable=False)
    hostname = db.Column(db.String(255), nullable=False)
    last_seen = db.Column(DateTime, nullable=False,
                          default=datetime.datetime.utcnow)
    first_seen = db.Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    updated_at = db.Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, mac_address, ipv4_address, hostname) -> None:
        self.mac_address = mac_address
        self.ipv4_address = ipv4_address
        self.hostname = hostname
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
    registered_on = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    active_account = db.Column(db.Boolean, nullable=False)

    @property
    def is_active(self):
        return self.active_account

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def __init__(self, username, password, name, is_active=False):
        self.username = username
        self.password = bcrypt.generate_password_hash(password, 12)
        self.name = name
        self.registered_on = datetime.datetime.now()
        self.active_account = is_active

    def __repr__(self):
        return "<User {}>".format(self.username)


class DeviceLinuxUpdateDetails(db.Model):
    __tablename__ = "device_linux_update_details"

    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), db.ForeignKey(
        "devices.mac_address"), nullable=False)
    package_name = db.Column(db.String(128), nullable=False)
    installed_version = db.Column(db.String(64), nullable=False)
    latest_version = db.Column(db.String(64), nullable=False)

    first_seen = db.Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    updated_at = db.Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, mac_address, pkgName, pkgVersion, pkgLatest):
        self.package_name = pkgName
        self.installed_version = pkgVersion
        self.latest_version = pkgLatest
        self.mac_address = mac_address


class DeviceWindowsUpdateDetails(db.Model):
    __tablename__ = "device_windows_update_details"

    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), db.ForeignKey(
        "devices.mac_address"), nullable=False)
    package_name = db.Column(db.String(128), nullable=False)
    installed_version = db.Column(db.String(64), nullable=True)
    latest_version = db.Column(db.String(64), nullable=False)
    is_installed = db.Column(db.Boolean, nullable=True)
    description = db.Column(db.String(1000), nullable=True)

    first_seen = db.Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    updated_at = db.Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def __init__(self, mac_address, pkgName, pkgVersion, pkgLatest, is_installed, description=None):
        self.package_name = pkgName
        self.installed_version = pkgVersion
        self.latest_version = pkgLatest
        self.mac_address = mac_address
        self.is_installed = is_installed
        self.description = description


class DevicePollingCommands(db.Model):
    __tablename__ = "device_polling_commands"

    command_id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.String(17), db.ForeignKey(
        "devices.mac_address"), nullable=False)
    command = db.Column(db.String(20), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    read_at = db.Column(DateTime, nullable=False,
                        default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
