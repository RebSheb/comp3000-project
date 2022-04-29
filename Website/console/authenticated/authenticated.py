from datetime import date
import datetime
from flask import render_template, Blueprint, flash
from flask_login import login_required
from flask_login.utils import logout_user
import flask_sqlalchemy
from sqlalchemy import func
from werkzeug.utils import redirect
from mac_vendor_lookup import MacLookup

# We need ARP (Address Resolution Protocol) to discover devices on our network
from scapy.all import ARP, Ether, srp
# We need socket to resolve hostnames by address and herror for HostnameError
from socket import gethostbyaddr, herror
from logging import log
from console import app, db
from console.models import Device, DeviceUpdateDetails, User

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
            # print("[{}] Last Seen: {} -> {}".format(existing_device.mac_address, existing_device.last_seen, datetime.datetime.utcnow()))
            existing_device.last_seen = datetime.datetime.utcnow()

        # To check if an agent is installed, we can simply perform a basic query against the deviceupdates table and check if an entry exists
        has_agent = DeviceUpdateDetails.query.filter_by(
            mac_address=device["mac"]).first()
        if has_agent:
            device["has_agent"] = "Installed"
        else:
            device["has_agent"] = "Not Available"

        try:
            device["tooltip"] = mac.lookup(device["mac"])
        except KeyError:
            device["tooltip"] = "Unknown Vendor"

    db.session.commit()

    return render_template("dashboard.jinja2", devices=devices)


@auth_bp.route("/about")
@login_required
def about():
    devices = Device.query.filter().all()
    agents = DeviceUpdateDetails.query.filter().group_by(
        DeviceUpdateDetails.mac_address).all()

    total_applications = DeviceUpdateDetails.query.filter().all()
    if total_applications != None and len(total_applications) > 0:
        available_to_update = 0
        for pkg in total_applications:
            if len(pkg.latest_version) > 0:
                available_to_update = available_to_update + 1
    return render_template("about.jinja2", number_of_devices=len(devices), ip_range=app.config["IP_RANGE"], number_of_agents=len(agents), total_applications=len(total_applications), available_to_update=available_to_update)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@auth_bp.route("/agent/<mac>/packages")
@login_required
def view_packages(mac):
    if mac != None:
        device = Device.query.filter(
            Device.mac_address.like(mac)).first()
        hostname = device.hostname
        # packages = DeviceUpdateDetails.query.filter(and_(
        #    DeviceUpdateDetails.mac_address.like(mac), ~func.coalesce(DeviceUpdateDetails.package_name, None))).order_by(DeviceUpdateDetails.package_name.asc()).all()
        packages = DeviceUpdateDetails.query.filter(
            DeviceUpdateDetails.mac_address.like(mac)).order_by(DeviceUpdateDetails.latest_version.desc()).all()
        if packages != None and len(packages) > 0:
            available_to_update = 0
            for pkg in packages:
                if len(pkg.latest_version) > 0:
                    available_to_update = available_to_update + 1
            return render_template('packages.jinja2', mac=mac, host=hostname, packages=packages, pkg_count=(len(packages) - available_to_update), updates=available_to_update)

    flash("An error ocurred looking up that MAC")
    return render_template('packages.jinja2')


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


@auth_bp.route("/admin/users")
@login_required
def user_management_console():
    users = User.query.with_entities(User.id,
                                     User.username, User.name, User.active_account).all()
    return render_template("user_management.jinja2", users=users)


@auth_bp.route("/admin/user/<user_id>/activate", methods=["POST"])
@login_required
def activate_user(user_id: int):
    print("[User Management] - Request received to activate user with ID: {}".format(user_id))
    user = User.query.get(user_id)
    if user is not None:
        user.active_account = True
    else:
        return "", 500
    db.session.commit()
    return "", 200


@auth_bp.route("/admin/user/<user_id>/deactivate", methods=["POST"])
@login_required
def deactivate_user(user_id: int):
    print("[User Management - Request received to deactivate user with ID: {}".format(user_id))
    user = User.query.get(user_id)
    activated_users = User.query.filter(User.active_account == True).all()
    if len(activated_users) <= 1:
        return "", 500
    if user is not None:
        user.active_account = False
    else:
        return "", 500

    db.session.commit()
    return "", 200


@auth_bp.route("/admin/user/<user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id: int):
    print("[User Management] - Request received to delete user with ID: {}".format(user_id))
    if len(User.query.all()) >= 1:
        return "", 500
    user = User.query.get(user_id)
    if user is not None:
        db.session.delete(user)
    else:
        return "", 500
    db.session.commit()
    return "", 200
