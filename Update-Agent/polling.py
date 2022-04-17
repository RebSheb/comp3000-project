import threading
import time
import logging
import requests
import json
from base_classes import UpdateHandler


class Polling(threading.Thread):
    def __init__(self, api_endpoint: str, api_port: int, frequency: int, update_handler: UpdateHandler):
        self.api_endpoint = api_endpoint
        self.api_port = api_port
        self.frequency = frequency
        self.update_handler = update_handler
        super(Polling, self).__init__()

    def run(self):
        while True:
            logging.info("Polling - Polling for commands...")
            self.poll_for_command()
            logging.info(
                "Polled - Sleeping for {} seconds".format(self.frequency))
            time.sleep(self.frequency)

    def poll_for_command(self):
        try:
            full_endpoint = self.api_endpoint + ":" + str(self.api_port) + "/agent/" + \
                self.update_handler.mac.lower() + "/commands"
            logging.info("Querying {}".format(full_endpoint))
            response = requests.get(full_endpoint)
            if response.status_code == 200:
                if response.json()["command"] == "update":
                    logging.info("Received update command, performing update.")
                    self.update_handler.perform_update()
                elif response.json()["command"] == "no_command":
                    logging.info(
                        "Received no command from webserver, sleeping.")
                else:
                    logging.error("Received unknown command from webserver!")

        except AttributeError as err:
            print(err)
            return
