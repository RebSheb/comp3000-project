import logging
import requests
# https://stackoverflow.com/questions/159137/getting-mac-address
from uuid import getnode as get_mac
import json


class UpdateHandler():
    def __init__(self, api_endpoint, api_port):
        logging.info("UpdatedHandler instantiated")
        self.api_endpoint = api_endpoint
        self.api_port = api_port
        self.mac = None

    def check_for_updates(self):
        pass

    def perform_update(self):
        pass

    def post_data(self, mac_address: str = None, data_to_post: list = None):
        if data_to_post is None:
            return ("Data to post is None!", False)
        if mac_address is None:
            return ("Mac Address is None!", False)

        # Format of the list should be like this for Linux
        # [ {"PkgName": "python3", "PkgVersion": "3.9.7", "PkgLatest": "3.9.8"} ]
        # For Windows
        # [ {"PkgName": "Security Intelligence Update for Microsoft Defender Antivirus - KB2267602 (Version 1.359.191.0)", "PkgLatest": "3.9.8", "PkgDescription": "Blah Blah"} ]
        self.mac = mac_address
        data = {
            "mac_address": mac_address,
            "data": data_to_post
        }
        data = json.dumps(data)
        try:
            if len(data_to_post) > 0:
                requests.post(str(self.api_endpoint) + ":" +
                              str(self.api_port) + "/agent/post_data", json=data)
        except Exception as error:
            logging.error(error)
            return (str(error), False)
