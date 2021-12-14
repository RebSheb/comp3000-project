from ..app import db, bcrypt
import datetime

class Device(db.Model):
    def __init__(self, mac_address, ip_address,) -> None:
        return