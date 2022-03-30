import threading
import time
import logging
import requests
from base_classes import UpdateHandler


class Polling(threading.Thread):
    def __init__(self, api_endpoint: str, frequency: int, update_handler: UpdateHandler):
        self.api_endpoint = api_endpoint
        self.frequency = frequency
        self.update_handler = update_handler
        super(Polling, self).__init__()

    def run(self):
        while True:
            logging.info("Polling for commands...")
            time.sleep(self.frequency)

    def poll_for_command(self):
        requests.get(self.api_endpoint + "/agents/" +
                     self.update_handler.mac.lower() + "/commands")
        pass
