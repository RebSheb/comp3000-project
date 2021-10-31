from base_classes import UpdateHandler
import logging
import apt


class LinuxUpdater(UpdateHandler):
    def __init__(self):
        super()
        logging.info("Linux Updater instantiated")

    def check_for_updates(self):
        upgradable_pkgs = {}
        logging.info("LinuxUpdater-CheckingForUpdates")
        cache = apt.Cache()
        cache.update()
        cache.open()
        for pkg in cache:
            if pkg.is_upgradable:
                logging.info("Package [{}] is upgradable from version [{}] to [{}]".format(pkg.name,
                                                                                           pkg.installed.version,
                                                                                           pkg.candidate.version))
                upgradable_pkgs[pkg.name] = {
                    "installed_version": pkg.installed.version, "available_version": pkg.candidate.version}

        print(upgradable_pkgs)
