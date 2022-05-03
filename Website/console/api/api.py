from flask import render_template, Blueprint, request, jsonify
from flask_login import login_required
from flask_login.utils import logout_user
from sqlalchemy import desc
from werkzeug.utils import redirect
from console import app, db
from console.models import DevicePollingCommands, DeviceLinuxUpdateDetails, DeviceWindowsUpdateDetails
import json

api_bp = Blueprint("api_bp", __name__)


@app.route("/agent/linux_post_data", methods=["POST"])
def do_linux_post_data():
    post_data = json.loads(request.json)
    try:
        for pkg in post_data["data"]:
            existing_update_details = DeviceLinuxUpdateDetails.query.filter_by(
                mac_address=post_data["mac_address"].lower(),
                package_name=pkg["PkgName"]
            ).first()

            if existing_update_details == None:  # Our mac_address and pkgName combo doesn't exist, let's add it
                new_linux_device_updates = DeviceLinuxUpdateDetails(
                    mac_address=post_data["mac_address"].lower(), pkgName=pkg["PkgName"],
                    pkgVersion=pkg["PkgVersion"], pkgLatest=pkg["PkgLatest"])

                db.session.add(new_linux_device_updates)

            else:  # Our package already exists, we need to compare versions to check if an update to the DB needs to be made
                existing_update_details.latest_version = pkg["PkgLatest"]
                existing_update_details.installed_version = pkg["PkgVersion"]

        db.session.commit()

    except KeyError as err:
        print(err)
        return '', 202
    return '', 200


@app.route("/agent/windows_post_data", methods=["POST"])
def do_windows_post_data():
    post_data = json.loads(request.json)
    try:
        for pkg in post_data["data"]:
            existing_update_details = DeviceWindowsUpdateDetails.query.filter_by(
                mac_address=post_data["mac_address"].lower(),
                package_name=pkg["PkgName"]
            ).first()

            if existing_update_details == None:
                new_windows_device_updates = DeviceWindowsUpdateDetails(
                    mac_address=post_data["mac_address"].lower(), pkgName=pkg["PkgName"],
                    pkgVersion=pkg["PkgVersion"], pkgLatest=pkg["PkgLatest"], is_installed=pkg["is_installed"],
                    description=pkg["PkgDescription"]
                )

                db.session.add(new_windows_device_updates)
            else:
                if existing_update_details.is_installed != None:
                    existing_update_details.is_installed = pkg["is_installed"]

                existing_update_details.latest_version = pkg["PkgLatest"]
                existing_update_details.installed_version = pkg["PkgVersion"]

        db.session.commit()

    except KeyError as err:
        print(err)
        return '', 202
    return '', 200


@app.route("/agent/<mac>/commands", methods=["GET"])
def do_get_commands(mac: str):
    return_data = {"command": "no_command"}
    device_command = DevicePollingCommands.query.filter_by(
        mac_address=mac.lower(), is_read=False).first()
    if device_command is not None:
        # We can return a command
        device_command.is_read = True
        return_data = {"command": device_command.command}

    db.session.commit()
    return jsonify(return_data)


@app.route("/agent/<mac>/commands", methods=["POST"])
def do_post_commands(mac: str):
    return_data = {"status": "success",
                   "msg": "Command to update device {} queued successfully".format(mac)}
    try:
        post_data = request.json
        device_command = DevicePollingCommands(
            mac_address=mac, command=post_data["command"])
        db.session.add(device_command)
        db.session.commit()
    except Exception as err:
        print("Error occured pushing UPDATE command for {mac}".format(mac))
        return_data["status"] = "failed"
        return_data["msg"] = "Failed to queue update command for device, please try again later."

    return jsonify(return_data)
