import logging
import socket


class Communication(object):
    def __init__(self):
        logging.info("Created communication")
        self.model = None
        self.host = None
        self.port = None
        self.socket = None

    def __del__(self):
        if self.socket is not None:
            self.socket.close()
            logging.info("Killing socket on exit.")

    def set_model(self, model):
        self.model = model
        logging.info('Appended model %s.', model)

    def prepare_connection(self, host, port):
        logging.info("Creating connection to %s:%s", host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.socket is None:
            logging.error("Failed to create socket.")
        try:
            self.socket.connect((host, port))
            logging.info("Successfully connected to host.")
        except (ConnectionRefusedError, socket.timeout) as e:
            logging.error("Failed to connect to host. %s", e)
            self.socket = None

    def send(self, msg):
        if self.socket is None:
            logging.warning("Will not send message, socket does not exist.")
            return
        self.socket.sendall(msg)

    def receive(self, size):
        if self.socket is None:
            logging.warning("Will not receive message, socket does not exist.")
            return None
        return self.socket.recv(size)






