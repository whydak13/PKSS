import logging

from exchanger import model, communication

logging_level = logging.DEBUG

def init_logger():
    format_style = '%(asctime)s %(levelname)s %(filename)s: %(message)s'
    logging.basicConfig(format=format_style, level=logging_level)
    logging.info("Initialized logger")


def main():
    host = '127.0.0.1'
    port = 80
    init_logger()
    exchanger = model.Model()
    exchanger.tick(21)
    communicator = communication.Communication()
    communicator.set_model(exchanger)
    communicator.prepare_connection(host, port)
    communicator.run()
if __name__ == '__main__':
    main()
