import logging
import socket
from exchanger.utils.json_builder import jsonBuilder as JsonBuilder


class Communication(object):
    def __init__(self, role=None):
        logging.info("Created communication")
        self.model = None
        self.host = None
        self.port = None
        self.socket = None

        self.role = role if role is not None else "wymiennik"
        self.json_builder = JsonBuilder(self.role)

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

    def send_init(self):
        self.json_builder.switch_to_init_json(self.role)
        self.__send(self.json_builder.serialize())

    def send_data(self):
        self.json_builder.switch_to_data_json(self.role)
        for k, v in self.model.get_parameters().items():
            self.json_builder.add_field(k, v)
        self.__send(self.json_builder.serialize())

    def __send(self, msg):
        logging.debug('Sending msg=%s to server.', msg)
        if self.socket is None:
            logging.warning("Will not send message, socket does not exist.")
            return
        self.socket.sendall(msg)

    def receive(self, size):
        if self.socket is None:
            logging.warning("Will not receive message, socket does not exist.")
            return None
        return self.socket.recv(size)

