from base_classes import UpdateHandler
import logging
import apt


class LinuxUpdater(UpdateHandler):
    def __init__(self, api_endpoint, api_port):
        super().__init__(api_endpoint, api_port)
        logging.info("Linux Updater instantiated")

    def check_for_updates(self):
        upgradable_pkgs = []
        logging.info("LinuxUpdater-CheckingForUpdates")
        cache = apt.Cache()
        cache.update()
        cache.open()
        for pkg in cache:
            if pkg.is_upgradable:
                logging.info("Package [{}] is upgradable from version [{}] to [{}]".format(pkg.name,
                                                                                           pkg.installed.version,
                                                                                           pkg.candidate.version))
                upgradable_pkgs.append(
                    {"PkgName": pkg.name, "PkgVersion": pkg.installed.version, "PkgLatest": pkg.candidate.version})

        self.post_data(upgradable_pkgs)
