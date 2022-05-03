import logging


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
        pass
