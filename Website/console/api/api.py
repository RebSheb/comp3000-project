from flask import render_template, Blueprint, request
from flask_login import login_required
from flask_login.utils import logout_user
from werkzeug.utils import redirect
from console import app, db
from console.models import DeviceUpdateDetails
from sqlalchemy import and_
import json

api_bp = Blueprint("api_bp", __name__)


@app.route("/agent/post_data", methods=["POST"])
def do_post_data():
    post_data = json.loads(request.json)
    try:
        for pkg in post_data["data"]:
            existing_update_details = DeviceUpdateDetails.query.filter_by(
                mac_address=post_data["mac_address"].lower(),
                package_name=pkg["PkgName"]
            ).first()

            if existing_update_details == None:  # Our mac_address and pkgName combo doesn't exist, let's add it
                new_device_updates = DeviceUpdateDetails(
                    mac_address=post_data["mac_address"].lower(), pkgName=pkg["PkgName"],
                    pkgVersion=pkg["PkgVersion"], pkgLatest=pkg["PkgLatest"])
                # Windows check
                if "PkgDescription" in pkg.keys():
                    new_device_updates.description = pkg["PkgDescription"]
                db.session.add(new_device_updates)

            else:  # Our package already exists, we need to compare versions to check if an update to the DB needs to be made
                existing_update_details.latest_version = pkg["PkgLatest"]
                existing_update_details.installed_version = pkg["PkgVersion"]

        db.session.commit()

    except KeyError as err:
        print(err)
        return '', 202
    return '', 200
