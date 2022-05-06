from cgitb import html
from datetime import date
import datetime
from flask import render_template, Blueprint, flash, jsonify, url_for, request, send_from_directory
from flask_login import login_required
from flask_login.utils import logout_user
from werkzeug.utils import redirect
from mac_vendor_lookup import MacLookup
# Used for zipping up agent directory
from shutil import make_archive
from os import path
# We need ARP (Address Resolution Protocol) to discover devices on our network
from scapy.all import ARP, Ether, srp
# We need socket to resolve hostnames by address and herror for HostnameError
from socket import gethostbyaddr, gethostbyname, gethostname, herror
from logging import log, shutdown
from console import app, db
from console.models import Device, DeviceLinuxUpdateDetails, DeviceWindowsUpdateDetails, User
from console.routes import login

auth_bp = Blueprint("authenticated", __name__, template_folder="templates")

mac = MacLookup()
mac.update_vendors()


@auth_bp.route("/")
@login_required
def home():
    return render_template("dashboard.jinja2")


@auth_bp.route("/device_scan")
@login_required
def do_network_scan():
    html_output = ""
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
        has_agent = DeviceLinuxUpdateDetails.query.filter_by(
            mac_address=device["mac"]).first()
        if not has_agent:
            has_agent = DeviceWindowsUpdateDetails.query.filter_by(
                mac_address=device["mac"]).first()
        if has_agent:
            device["has_agent"] = "Installed"
        else:
            device["has_agent"] = "Not Available"

        try:
            device["tooltip"] = mac.lookup(device["mac"])
        except KeyError:
            device["tooltip"] = "Unknown Vendor"
        html_output = html_output + "<tr>"
        html_output = html_output + "<td data-toggle='tooltip' data-placement='top' title={tooltip}>{mac}</td>".format(
            tooltip=device["tooltip"], mac=device["mac"])
        html_output = html_output + \
            "<td>{hostname}</td>".format(hostname=device["hostname"])
        html_output = html_output + "<td>{ip}</td>".format(ip=device["ip"])
        html_output = html_output + \
            "<td>{has_agent}</td>".format(has_agent=device["has_agent"])
        html_output = html_output + "<td>"
        if device["has_agent"] == "Installed":
            html_output = html_output + "<a href='" + \
                url_for("authenticated.view_packages",
                        mac=device["mac"]) + "' role='button' class='btn btn-primary'>Packages</a>"
        else:
            html_output = html_output + "No Options Available"

        html_output = html_output + "</td>"
        html_output = html_output + "</tr>"

    db.session.commit()
    return html_output


@auth_bp.route("/about")
@login_required
def about():
    devices = Device.query.filter().all()
    linux_agents = DeviceLinuxUpdateDetails.query.filter().group_by(
        DeviceLinuxUpdateDetails.mac_address).all()
    windows_agents = DeviceWindowsUpdateDetails.query.filter().group_by(
        DeviceWindowsUpdateDetails.mac_address).all()

    total_linux_applications = DeviceLinuxUpdateDetails.query.filter().all()
    total_windows_applications = DeviceWindowsUpdateDetails.query.filter().all()

    available_to_update = 0
    if total_linux_applications != None and len(total_linux_applications) > 0:
        for pkg in total_linux_applications:
            if len(pkg.latest_version) > 0:
                available_to_update = available_to_update + 1

    if total_windows_applications != None and len(total_windows_applications) > 0:
        for pkg in total_windows_applications:
            if len(pkg.latest_version) > 0:
                available_to_update = available_to_update + 1

    return render_template("about.jinja2", number_of_devices=len(devices), ip_range=app.config["IP_RANGE"], number_of_agents=len(linux_agents) + len(windows_agents), total_applications=len(total_linux_applications) + len(total_windows_applications), available_to_update=available_to_update)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")


@auth_bp.route("/help")
@login_required
def help_page():
    return render_template("help.jinja2")


@auth_bp.route("/agent/<mac>/packages")
@login_required
def view_packages(mac):
    if mac != None:
        device = Device.query.filter(
            Device.mac_address.like(mac)).first()
        hostname = device.hostname
        linux_packages = None
        windows_packages = None
        linux_packages = DeviceLinuxUpdateDetails.query.filter(
            DeviceLinuxUpdateDetails.mac_address.like(mac)).order_by(DeviceLinuxUpdateDetails.latest_version.desc()).all()
        windows_packages = DeviceWindowsUpdateDetails.query.filter(
            DeviceWindowsUpdateDetails.mac_address.like(mac)).order_by(DeviceWindowsUpdateDetails.latest_version.desc()).all()

        if linux_packages == []:
            packages = windows_packages
        else:
            packages = linux_packages

        if packages != None and len(packages) > 0:
            available_to_update = 0
            for pkg in packages:
                try:
                    if type(pkg) == DeviceWindowsUpdateDetails:
                        if pkg.is_installed == 0:
                            available_to_update = available_to_update + 1
                            continue
                except KeyError:
                    pass
                if len(pkg.latest_version) > 0:
                    available_to_update = available_to_update + 1

            return render_template('packages.jinja2', mac=mac, host=hostname, packages=packages, pkg_count=(len(packages) - available_to_update), updates=available_to_update)

    flash("An error ocurred looking up that MAC")
    return render_template('packages.jinja2')


@auth_bp.route("/agent/download", methods=["GET"])
@login_required
def download_agent():
    agent_path = path.join(app.root_path, "../../")
    # normpath resolves the ../ dir changes
    agent_path = path.join(path.normpath(agent_path), "Update-Agent")
    print(request.host)

    make_archive("agent", format="zip", root_dir=agent_path)
    return send_from_directory(directory=path.normpath(path.join(app.root_path, "..")), filename="agent.zip")


@auth_bp.route("/admin/users")
@login_required
def user_management_console():
    users = User.query.with_entities(User.id,
                                     User.username, User.name, User.active_account).all()
    return render_template("user_management.jinja2", users=users)


@auth_bp.route("/admin/user/<user_id>/activate", methods=["POST"])
@login_required
def activate_user(user_id: int):
    return_data = {"status": "success",
                   "msg": "Successfully activated that user!"}
    print("[User Management] - Request received to activate user with ID: {}".format(user_id))
    user = User.query.get(user_id)
    if user is not None:
        user.active_account = True
    else:
        return_data = {"status": "failed",
                       "msg": "This user could not be found!"}
    db.session.commit()
    return jsonify(return_data)


@auth_bp.route("/admin/user/<user_id>/deactivate", methods=["POST"])
@login_required
def deactivate_user(user_id: int):
    return_data = {"status": "success",
                   "msg": "Successfully deactivated that user!"}
    print("[User Management - Request received to deactivate user with ID: {}".format(user_id))
    user = User.query.get(user_id)
    activated_users = User.query.filter(User.active_account == True).all()
    if len(activated_users) <= 1:
        return_data = {"status": "failed",
                       "msg": "At least one user must remain active at all times!"}
    else:
        if user is not None:
            user.active_account = False
        else:
            return_data = {"status": "failed",
                           "msg": "This user could not be found!"}

    db.session.commit()
    return jsonify(return_data)


@auth_bp.route("/admin/user/<user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id: int):
    return_data = {"status": "success",
                   "msg": "Successfully deleted that user!"}
    print("[User Management] - Request received to delete user with ID: {}".format(user_id))
    if len(User.query.all()) <= 1:
        return_data["status"] = "failed"
        return_data["msg"] = "You cannot delete the last existing user!"

    else:
        user = User.query.get(user_id)
        if user is not None:
            db.session.delete(user)
        else:
            return_data["status"] = "failed"
            return_data["msg"] = "This user could not be found!"

    db.session.commit()
    return jsonify(return_data)


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
