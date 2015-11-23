import logging
import socket
from exchanger.utils.json_builder import jsonBuilder as JsonBuilder
from time import sleep


class Communication(object):

    TIME_KEY = 'trzy_miliony'

    def __init__(self, role=None):
        logging.info("Created communication")
        self.model = None
        self.host = None
        self.port = None
        self.socket = None

        self.role = role if role is not None else "wymiennik"
        self.json_builder = JsonBuilder(self.role)

        self.communication_tries = 20000

        self.time = 1

    def __del__(self):
        if self.socket is not None:
            self.socket.close()
            logging.info("Killing socket on exit.")

    def set_model(self, model):
        self.model = model
        self.model.set_start_time(self.time)
        logging.info('Appended model %s.', model)

    def prepare_connection(self, host, port):
        logging.info("Creating connection to %s:%s", host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.socket is None:
            logging.error("Failed to create socket.")

        for t in range(self.communication_tries):
            try:
                self.socket.connect((host, port))
                logging.info("Successfully connected to host.")
                break
            except (ConnectionRefusedError, socket.timeout) as e:
                logging.error("Failed to connect to host. %s", e)
            sleep(0.5)
        else:
            self.socket = None

    def run(self):
        if self.socket is None:
            logging.error("Socket does not exists, aborting!")
            return

        self.__send_init()
        js = self.__receive_init()
        try:
            self.time = js[Communication.TIME_KEY]
        except:
            logging.info('Using default value of time ' + str(self.time))
        while True:
            # sleep(1)
            self.__cycle0()

    def __cycle(self):
        self.__receive_time()
        self.model.tick(self.time)
        self.__send_data()
        self.__receive_data()
        logging.info("Tick complete")

    def __cycle0(self):
        # self.time += 1
        self.model.tick(self.time * 60)
        self.__send_data()
        self.__receive_data()
        logging.info("Tick complete")


    def __send_init(self):
        self.json_builder.switch_to_init_json(self.role)
        self.__send(self.json_builder.serialize())

    def __send_data(self):
        self.json_builder.switch_to_data_json(self.role)
        for k, v in self.model.get_state().items():
            self.json_builder.add_field(k, v)

        self.__send(self.json_builder.serialize())

    def __send(self, msg):
        logging.debug('Sending msg=%s to server.', msg)
        if self.socket is None:
            logging.warning("Will not send message, socket does not exist.")
            return

        for t in range(self.communication_tries):
            try:
                logging.info('Trying to send msg.')
                self.socket.sendall(bytes(msg, 'utf-8'))
                logging.debug('Msg sent.')
                break
            except Exception as e:
                logging.warning('Exception caught. ' + str(e))
                sleep(0.5)
        else:
            logging.error("Failed to send message.")

    def __receive(self, size=1024):
        if self.socket is None:
            logging.warning("Will not receive message, socket does not exist.")
            return None
        self.socket.setblocking(True)
        msg = self.socket.recv(size)
        logging.debug('Received bytes ' + str(msg))
        self.socket.setblocking(False)
        return msg

    def __receive_time(self):
        js = self.json_builder.deserialize(self.__receive())
        self.time = js['time']
        logging.info("Received time value %f", self.time)

    def __receive_init(self):
        js = self.json_builder.deserialize(self.__receive())
        logging.info('Init msg received. ' + str(js))
        return js

    def __receive_data(self):
        js = self.json_builder.deserialize(self.__receive())
        logging.debug('Received msg: ' + str(js))
        js.pop('type')
        if Communication.TIME_KEY in js.keys():
            self.time = js[Communication.TIME_KEY]
        self.model.update_parameters(js)

