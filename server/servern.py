#!/usr/bin/python

import logging
import socket
import select
import json

# TCP sockets parameters end

class Client:
    filters = []
    processed = False
    initialized = False

    def loadClientFromString(self, string):
        self.filters = string.split()
        if len(self.filters) != 0:
            return self.filters.pop(0)
        else:
            return ''

    @staticmethod
    def loadClientsFromFile(clientDict, clientsFilename):
        file = open(clientsFilename, 'r')
        line = file.readline()
        while line:
            if line.find('#') < 0:
                client = Client()
                name = client.loadClientFromString(line)
                if name != '':
                    clientDict[name] = client
                else:
                    logging.warning('Client file record invalid, loaded [%s]' % (line))
            line = file.readline()
        file.close()

    def filterJSON(self, clientName, jsonDict):
        if self.filters[0] != "!":
            jsonDictFiltered = {}
            for key in self.filters:
                value = jsonDict.get(key, None)
                if value != None:
                    jsonDictFiltered[key] = value
                else:
                    logging.warning('Client [%s] expecting [%s] parameter, but not provided' % (clientName, key))
            return jsonDictFiltered
        else:
            return jsonDict

class ServerManager:
    STD_FIELD_TYPE = 'type'
    TYPE_LOG = 'log'
    TYPE_DATA = 'data'
    TYPE_INIT = 'init'

    STD_FIELD_SRC = 'src'

    STD_FIELD_TIME = 'trzy_miliony'

    STD_FIELD_LOG_MSG = 'log_msg'

    RECEIVE_BUFFER = 4096
    HOST = '192.168.45.67'
    PORT = 1234

    STATE_INIT = 'init'
    STATE_SIMULATION_INIT = 'simulation_init'
    STATE_SIMULATION = 'simulation'
    STATE_SIMULATION_STOP = 'simulation_stop'

    clients = {}
    sockets = {}
    listener = None
    state = STATE_INIT
    globalJSON = {}
    globalTime = 0
    globalTimeIncrement = 10

    def __init__(self, clientsFilename):
        Client.loadClientsFromFile(self.clients, clientsFilename)
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((self.HOST, self.PORT))
        self.listener.listen(10)
        logging.info("Server started listening on port [%s]" % (str(self.PORT)))

    def clientsProcessedCount(self):
        processedCount = 0
        for client in self.clients.itervalues():
            if client.processed == True:
                processedCount += 1
        return processedCount

    def clearClientsProcessed(self):
        for client in self.clients.itervalues():
            client.processed = False

    def disconnectClient(self, clientSocket):
        partWarn = "Client [%s:%d], name [%s] disconnected"
        logging.info(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1], self.sockets[clientSocket]))
        client = self.clients.get(self.sockets[clientSocket], None)
        if client != None:
            client.processed = False
            client.initialized = False
        clientSocket.close()
        self.sockets.pop(clientSocket, None)

    def validateSrc(self, jsonSrc):
        return self.clients.keys().count(jsonSrc) > 0

    def insertTimeIncrement(self):
        gui_time = self.globalJSON.get(self.STD_FIELD_TIME, None)
        if gui_time != None:
            self.globalTimeIncrement = gui_time
        self.globalJSON[self.STD_FIELD_TIME] = self.globalTimeIncrement
        self.globalTime += self.globalTimeIncrement

    def insertType(self, type):
        self.globalJSON[self.STD_FIELD_TYPE] = type

    def allClientsConnected(self):
        return set(self.clients.keys()) == set(self.sockets.values())

    def broadcast_init(self):
        temp_json = {}
        temp_json[self.STD_FIELD_TYPE] = self.TYPE_INIT
        temp_json[self.STD_FIELD_TIME] = self.globalTimeIncrement
        serialized = json.dumps(temp_json)
        for clientSocket in self.sockets:
            client = self.clients[self.sockets[clientSocket]]
            if not client.initialized:
                msg = "Sending init Json to %s [%s:%d]: %s"
                msg = msg % (self.sockets[clientSocket], clientSocket.getpeername()[0], clientSocket.getpeername()[1], str(temp_json))
                logging.debug(msg)
                clientSocket.setblocking(True)
                clientSocket.sendall(serialized)
                clientSocket.setblocking(False)
                client.initialized = True
        
    def broadcast(self):
        logging.debug("Sending global JSON to all (%d) clients: %s" % (len(self.sockets), str(self.globalJSON)) )
        for clientSocket in self.sockets:
            serialized = json.dumps(self.globalJSON)
            clientSocket.setblocking(True)
            clientSocket.sendall(serialized)
            clientSocket.setblocking(False)

    def broadcastFiltered(self):
        logging.debug("Sending global JSON to all (%d) clients: %s" % (len(self.sockets), str(self.globalJSON)) )
        for clientSocket in self.sockets:
            client = self.clients[self.sockets[clientSocket]]
            filtered = client.filterJSON(self.sockets[clientSocket], self.globalJSON)
            serialized = json.dumps(filtered)
            clientSocket.setblocking(True)
            clientSocket.sendall(serialized)
            clientSocket.setblocking(False)

    def switchState(self, state):
        partDebug = 'Switching state from [%s] to [%s]. Client list: %s'
        logging.debug(partDebug % (self.state, state, str(self.sockets.values())))
        self.state = state
        
    def processJSON(self, clientSocket, jsonType, jsonSrc, jsonDict):
        # This function is called if valid JSON message with 'type' and 'src' fields was received
        if self.validateSrc(jsonSrc):
            if self.sockets[clientSocket] == '' or self.sockets[clientSocket] == jsonSrc:
                if jsonType == self.TYPE_INIT:
                    self.processInit(clientSocket, jsonSrc, jsonDict)
                elif jsonType == self.TYPE_LOG:
                    self.processLog(clientSocket, jsonSrc, jsonDict)
                elif jsonType == self.TYPE_DATA:
                    self.processData(clientSocket, jsonSrc, jsonDict)
                else:
                    partWarn = 'JSON received from [%s:%d] has invalid \'type\' field [%s]'
                    logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1], jsonType))
            else:
                partWarn = 'Client [%s:%d], name [%s] sent message with new name [%s]'
                logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1], self.sockets[clientSocket], jsonSrc))
        else:
            partWarn = 'JSON received from [%s:%d] has invalid \'src\' field [%s]'
            logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1], jsonSrc))
            partWarn = 'Expecting following \'src\' values %s'
            logging.warning(partWarn % (str(self.clients.keys())))
            self.disconnectClient(clientSocket)

    def processInit(self, clientSocket, jsonSrc, jsonDict):
        if self.state == self.STATE_INIT or self.state == self.STATE_SIMULATION_STOP:
            if self.sockets.values().count(jsonSrc) == 0:
                if self.sockets[clientSocket] == '':
                    self.sockets[clientSocket] = jsonSrc
                    partInfo = 'Client [%s:%d] introduced itself as [%s]'
                    logging.info(partInfo % (clientSocket.getpeername()[0], clientSocket.getpeername()[1], jsonSrc))
                else:
                    partWarn = 'Client [%s:%d], name [%s] provided multiple init messages'
                    logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1], jsonSrc))
                    self.disconnectClient(clientSocket)
            else:
                partWarn = 'Client [%s:%d], introduced itself as already introduced [%s]'
                logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1], jsonSrc))
                self.disconnectClient(clientSocket)
        else:
            partWarn = 'Client [%s:%d], name [%s] provided init messages while server is not in init state'
            logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1], jsonSrc))
            self.disconnectClient(clientSocket)

    def processLog(self, clientSocket, jsonSrc, jsonDict):
        logMsg = jsonDict.pop(self.STD_FIELD_LOG_MSG, None)
        if logMsg != None:
            logging.info('Log from [%s]: [%s]' % (jsonSrc, str(logMsg)))

    def processData(self, clientSocket, jsonSrc, jsonDict):
        if self.state == self.STATE_SIMULATION or self.state == self.STATE_SIMULATION_STOP:
            commonJSON = set(jsonDict.keys()).intersection(self.globalJSON.keys())
            if commonJSON:
                partWarn = 'Client [%s:%d], name [%s] overrides part of already received data: [%s]'
                logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1], jsonSrc, str(commonJSON)))
            self.globalJSON.update(jsonDict)
            self.clients[jsonSrc].processed = True
        else:
            partWarn = 'Received \'data\' type JSON, in initialization state, from [%s:%d], name [%s]'
            logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1], jsonSrc))

    def process(self):
        listeners,_,_ = select.select([self.listener],[],[], 0.1)
        for listener in listeners:
            listener.setblocking(False)
            clientSocket,_ = listener.accept()
            self.sockets[clientSocket] = ''
            logging.info("Client [%s:%d] connected" % (clientSocket.getpeername()[0], clientSocket.getpeername()[1]))

        if self.sockets.keys():
            socketsRead,_,_ = select.select(self.sockets.keys(),[],[], 1.0)
            for clientSocket in socketsRead:
                data = clientSocket.recv(self.RECEIVE_BUFFER)
                if data != '':
                    msg = "Received data from client %s [%s:%d]: %s"
                    msg = msg % (self.sockets[clientSocket], clientSocket.getpeername()[0], clientSocket.getpeername()[1], str(data))
                    logging.debug(msg)
                    try:
                        clientJSON = json.loads(str(data))
                        jsonType = clientJSON.pop(self.STD_FIELD_TYPE, None)
                        if jsonType != None:
                            jsonSrc = clientJSON.pop(self.STD_FIELD_SRC, None)
                            if jsonSrc != None:
                                self.processJSON(clientSocket, str(jsonType), str(jsonSrc), clientJSON)
                            else:
                                partWarn = 'JSON received from [%s:%d] has no \'src\' field'
                                logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1]))
                        else:
                            partWarn = 'JSON received from [%s:%d] has no \'type\' field'
                            logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1]))
                    except ValueError:
                        partWarn = 'String received from [%s:%d] is not JSON'
                        logging.warning(partWarn % (clientSocket.getpeername()[0], clientSocket.getpeername()[1]))
                        logging.warning('Received : [%s]' % str(data).strip('\n'))
                else:
                    self.disconnectClient(clientSocket)

        # State switcher
        if self.state == self.STATE_INIT:
            if self.allClientsConnected():
                self.switchState(self.STATE_SIMULATION_INIT)
                self.globalJSON.clear()
                self.insertTimeIncrement()
                self.insertType(self.TYPE_INIT)
                self.broadcast_init()
        if self.state == self.STATE_SIMULATION:
            if not self.allClientsConnected():
                self.switchState(self.STATE_SIMULATION_STOP)
            else:
                if self.clientsProcessedCount() == len(self.clients):
                    self.insertTimeIncrement()
                    self.insertType(self.TYPE_DATA)
                    self.broadcastFiltered()
                    self.switchState(self.STATE_SIMULATION_INIT)
        if self.state == self.STATE_SIMULATION_INIT:
            if not self.allClientsConnected():
                self.insertType(self.TYPE_INIT)
            else:
                self.clearClientsProcessed()
                self.globalJSON.clear()
                self.switchState(self.STATE_SIMULATION)
        if self.state == self.STATE_SIMULATION_STOP:
            if not self.allClientsConnected():
                self.switchState(self.STATE_SIMULATION_STOP)
            else:
                self.switchState(self.STATE_SIMULATION)
                self.broadcast_init()

# Main
if __name__ == "__main__":
    logging.basicConfig(format = '%(levelname)s %(filename)s: %(message)s', level = logging.DEBUG)
    communicationManager = ServerManager('clients_test.txt')

    while True:
        communicationManager.process()
