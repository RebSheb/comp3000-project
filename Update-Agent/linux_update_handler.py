from base_classes import UpdateHandler
import logging
import apt
import netifaces
import requests
import json


class LinuxUpdater(UpdateHandler):
    def __init__(self, api_endpoint, api_port):
        super().__init__(api_endpoint, api_port)
        logging.info("Linux Updater instantiated")

    def check_for_updates(self):
        try:
            upgradable_pkgs = []
            logging.info("LinuxUpdater-CheckingForUpdates")
            cache = apt.Cache()
            cache.update()
            cache.open()
            for pkg in cache:
                if pkg.is_upgradable:
                    # logging.info("Package [{}] is upgradable from version [{}] to [{}]".format(pkg.name,
                    #                                                                           pkg.installed.version,
                    #                                                                           pkg.candidate.version))
                    upgradable_pkgs.append(
                        {"PkgName": pkg.name, "PkgVersion": pkg.installed.version, "PkgLatest": pkg.candidate.version})
                else:
                    if pkg != None and pkg.installed != None:
                        upgradable_pkgs.append(
                            {"PkgName": pkg.name, "PkgVersion": pkg.installed.version, "PkgLatest": ""})

            mac = netifaces.ifaddresses("eth0")[netifaces.AF_LINK][0]["addr"]
            self.post_data(mac, upgradable_pkgs)
        except Exception as error:
            print(error)
            logging.error(
                "An error occured while attempting to check for updates, is an update in progress or is the agent ran as root?")
            return

    def perform_update(self):
        logging.info("LinuxUpdater-PerformUpdate - It's time to update!")
        cache = apt.Cache()
        cache.update()
        cache.open()
        cache.upgrade()
        logging.info("Upgrade finalizing; commiting to cache")
        cache.commit()
        logging.info("Upgrade complete")

    def post_data(self, mac_address: str = None, data_to_post: list = None):
        if data_to_post is None:
            return ("Data to post is None!", False)
        if mac_address is None:
            return ("Mac Address is None!", False)

        self.mac = mac_address
        data = {
            "mac_address": mac_address,
            "data": data_to_post
        }
        data = json.dumps(data)
        try:
            if len(data_to_post) > 0:
                requests.post(str(self.api_endpoint) + ":" +
                              str(self.api_port) + "/agent/linux_post_data", json=data)
        except Exception as error:
            logging.error(error)
            return (str(error), False)

# https://www.python.org/ftp/python/3.10.4/python-3.10.4-amd64.exe
