import logging
from base_classes import UpdateHandler


class WindowsUpdater(UpdateHandler):
    def __init__(self):
        super(self)
        logging.info("Windows Updated instantiated")
