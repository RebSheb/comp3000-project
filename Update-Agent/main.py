import json  # For eventually compiling data into a JSON object to send to API
import time  # For sleeping
import logging
import configparser
import sys
from polling import Polling


def main():
    while True:
        # In here is where we call functions to do primary
        # agent logic.
        # We need to keep an updated list of installed packages
        # And inside each installed package we should check the 'is_upgradable' flag
        # if upgradable, add it to a list which will be compiled and shipped to API
        # Also have a polling thread created which checks the API to see if any commands
        # to update said package are available.
        logging.info("Updating Apt Cache")
        # apt_Cache.update()
        logging.info("Checking for available updates")
        # pkgs = apt_Cache.open()
        # for package in pkgs:
        #    if package.is_upgradable:
        #        logging.info("Package [{}] is upgradable from version [{}] to [{}]".format(package.name,
        #         package.installed.version,
        #         package.candidate.version))
        logging.info("Done, waiting 30 seconds...")
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


def create_poller_thread(poller_endpoint: str, frequency: int):
    polling_thread = Polling(poller_endpoint, frequency)
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
        if config is not None:
            create_poller_thread(config["POLLER"]["API_ENDPOINT"], int(
                config["POLLER"]["FREQUENCY"]))
        else:
            logging.error(
                "Configuration file 'agent.conf' not available, exiting...")
            sys.exit(-1)
    except Exception as error:
        logging.error(error)
        logging.error(
            "Linux-Agent cannot recover from this exception, exiting...")
        sys.exit(-1)

    main()
