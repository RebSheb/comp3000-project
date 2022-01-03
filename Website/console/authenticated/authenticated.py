from flask import render_template, Blueprint, flash
from flask_login import login_required
from flask_login.utils import logout_user
from werkzeug.utils import redirect

# We need ARP (Address Resolution Protocol) to discover devices on our network
from scapy.all import ARP, Ether, srp

auth_bp = Blueprint("authenticated", __name__, template_folder="templates")


@auth_bp.route("/")
@login_required
def home():
    clients = []
    try:
        target_ip = "192.168.1.1/24"
        arp = ARP(pdst=target_ip)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        result = srp(packet, timeout=3)[0]
        clients = []
        for sent, received in result:
            clients.append({'ip': received.psrc, 'mac': received.hwsrc})
    except PermissionError as err:
        flash("A PermissionError error occurred in LANMan! Is it running ")

    return render_template("dashboard.jinja2", devices=clients)


@auth_bp.route("/about")
@login_required
def about():
    return render_template("about.jinja2")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")
