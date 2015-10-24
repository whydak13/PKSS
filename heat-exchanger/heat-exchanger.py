import logging
import time

import model
import communication


def init_logger():
    format = '%(asctime)s %(levelname)s %(filename)s: %(message)s'
    logging.basicConfig(format=format, level=logging.INFO)
    logging.info("Initialized logger")


def main():
    host = '127.0.0.1'
    port = 80
    init_logger()
    exchanger = model.Model()
    while True:
        exchanger.tick(1, 1)
        time.sleep(0.1)
    # communicator = communication.Communication()
    # communicator.set_model(exchanger)
    # communicator.prepare_connection(host, port)
    # communicator.send("msg")

if __name__ == '__main__':
    main()
