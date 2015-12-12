import logging

from exchanger import model, communication

'''
todo
strumienie - tony na godzinę -> przekształcam po swojej stronie
'''
logging_level = logging.DEBUG

def init_logger():
    format_style = '%(asctime)s %(levelname)s %(filename)s: %(message)s'
    logging.basicConfig(format=format_style, level=logging_level)
    logging.info("Initialized logger")


def main():
    host = '192.168.45.67'
    # host = 'localhost'
    port = 1234
    init_logger()
    exchanger = model.Model()

    communicator = communication.Communication()
    communicator.set_model(exchanger)
    communicator.prepare_connection(host, port)
    communicator.run()

if __name__ == '__main__':
    main()
