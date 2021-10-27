from .base_classes import UpdateHandler
import logging

class LinuxUpdater(UpdateHandler):
    def __init__(self):
        super(self)
        logging.info("Linux Updated instantiated")