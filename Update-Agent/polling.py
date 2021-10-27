import threading
import time
import logging

class Polling(threading.Thread):
    def __init__(self, api_endpoint : str, frequency : int):
        self.api_endpoint = api_endpoint
        self.frequency = frequency
        super(Polling, self).__init__()

    def run(self):
        while True:
            logging.info("Polling for commands...")
            time.sleep(self.frequency)