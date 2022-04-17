import json  # For eventually compiling data into a JSON object to send to API
import time  # For sleeping
import logging
import configparser
import sys
from base_classes import UpdateHandler
from polling import Polling


def main(config):

    if sys.platform == "linux":
        from linux_update_handler import LinuxUpdater as updater
    elif sys.platform == "win32":
        from windows_update_handler import WindowsUpdater as updater
    else:
        logging.error("Unknown sys.platform! Exiting...")
        sys.exit(-2)

    update_handler = updater(
        config["AGENT"]["API_ENDPOINT"], config["AGENT"]["API_PORT"])

    create_poller_thread(config["AGENT"]["API_ENDPOINT"], config["AGENT"]["API_PORT"], int(
        config["POLLER"]["FREQUENCY"]), update_handler)

    while True:
        update_handler.check_for_updates()

        logging.info("Done checking for updates, waiting 30 seconds...")
        time.sleep(30)


def read_agent_configuration():
    config = None
    try:
        configuration_path = "./agent.conf"
        config = configparser.ConfigParser()
        config.read(configuration_path)
    except configparser.Error as err:
        logging.error("There was an error parsing agent.conf")
        logging.error(err)

    return config


def create_poller_thread(poller_endpoint: str, poller_port: int, frequency: int, update_handler: UpdateHandler):
    polling_thread = Polling(
        poller_endpoint, poller_port, frequency, update_handler)
    polling_thread.daemon = True  # Terminate on mainthread death
    polling_thread.start()
    logging.info("Polling thread created successfully")
    return


if __name__ == "__main__":
    print("[+] - Agent starting...")
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("Logging configuration level set")

    config = read_agent_configuration()
    try:
        if config is None:
            logging.error(
                "Configuration file 'agent.conf' not available, exiting...")
            sys.exit(-1)

    except Exception as error:
        logging.error(error)
        logging.error(
            "Agent cannot recover from this exception, exiting...")
        sys.exit(-1)

    main(config)
