from datetime import date
import datetime
from flask import render_template, Blueprint, flash
from flask_login import login_required
from flask_login.utils import logout_user
from werkzeug.utils import redirect
from mac_vendor_lookup import MacLookup

# We need ARP (Address Resolution Protocol) to discover devices on our network
from scapy.all import ARP, Ether, srp
# We need socket to resolve hostnames by address and herror for HostnameError
from socket import gethostbyaddr, herror
from logging import log
from console import app, db
from console.models import Device

auth_bp = Blueprint("authenticated", __name__, template_folder="templates")

mac = MacLookup()
mac.update_vendors()


@auth_bp.route("/")
@login_required
def home():
    devices = network_scan()
    for device in devices:
        # print("[Looking at] {} : {} : {}".format(
        #   device["mac"], device["ip"], device["hostname"]))
        new_device = Device(device["mac"], device["ip"], device["hostname"])
        if Device.query.filter_by(mac_address=device["mac"]).first() == None:
            db.session.add(new_device)
        else:
            existing_device = Device.query.get(device["mac"])
            #print("[{}] Last Seen: {} -> {}".format(existing_device.mac_address, existing_device.last_seen, datetime.datetime.utcnow()))
            existing_device.last_seen = datetime.datetime.utcnow()
        device["tooltip"] = mac.lookup(device["mac"])

    db.session.commit()

    return render_template("dashboard.jinja2", devices=devices)


@auth_bp.route("/about")
@login_required
def about():
    return render_template("about.jinja2")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


def network_scan():
    clients = []
    try:
        target_ip = app.config["IP_RANGE"]
        arp = ARP(pdst=target_ip)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        result = srp(packet, timeout=1)[0]
        clients = []
        for sent, received in result:
            try:
                hostname = ""
                (hostname, alias, ip) = gethostbyaddr(received.psrc)
            except herror:
                hostname = "Unknown Hostname"

            clients.append(
                {'ip': received.psrc, 'mac': received.hwsrc, "hostname": hostname})

        if len(clients) == 0:
            flash("No devices found on network!")

    except PermissionError as err:
        flash("A PermissionError error occurred in LANMan! Is it running as root or does it have permission?")

    return clients
