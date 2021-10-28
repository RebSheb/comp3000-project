import logging
from base_classes import UpdateHandler


class WindowsUpdater(UpdateHandler):
    def __init__(self):
        super()
        logging.info("Windows Updater instantiated")

    def check_for_updates(self):
        logging.info("WindowsUpdater-CheckingForUpdates")
