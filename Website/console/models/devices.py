from ..app import db
from sqlalchemy import DateTime
from sqlalchemy.
import datetime

class Device(db.Model):

    mac_address = db.Column(db.Integer, primary_key=True)
    ipv4_address = db.Column(db.String(15), nullable=False)
    last_seen = db.Column(DateTime, default=datetime.datetime.now())
    first_seen = db.COlumn(DateTime, default=datetime.datetime.now())

    def __init__(self, mac_address, ipv4_address) -> None:
        self.mac_address = mac_address
        self.ip_address = ipv4_address
        return

    def __repr__(self):
        return "<Device %r" % self.mac_address