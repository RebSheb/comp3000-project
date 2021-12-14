from ..app import db, bcrypt
import datetime

class Device(db.Model):

    mac_address = db.Column(db.Integer, primary_key=True)
    ipv4_address = db.Column(db.String(15), nullable=False)

    def __init__(self, mac_address, ipv4_address) -> None:
        self.mac_address = mac_address
        self.ip_address = ipv4_address
        return

    def __repr__(self):
        return "<Device %r" % self.mac_address