#include "ConnectionManager.h"
#include "LoggerWrapper.h"
#include <algorithm>
#include <iostream>
#include <thread>

/**********************************************************************
* ConnectionManager::ConnectedNode methods
**********************************************************************/

bool ConnectionManager::ConnectedNode::operator==(const ConnectedNode & rop) const {
    return name == rop.name;
}

/**********************************************************************
* ConnectionManager methods
**********************************************************************/

void ConnectionManager::poolConnection() {
    static sf::TcpSocket * newSocket = new sf::TcpSocket;
    static const std::string nameReqest = "{\"type\":\"data\",\"src\":\"\"}";
    switch (socketListener.accept(*newSocket)) {
    case sf::TcpListener::Status::Done: {
        ConnectedNode node { "", newSocket };
        LW_LOG(LW_INFO, "Established connection addr:port[name] - " << connectionInfo(node));
        connections.push_back(node);
        sendData(newSocket, nameReqest.c_str(), nameReqest.size());
        newSocket = new sf::TcpSocket;
        break;
    }
    case sf::TcpListener::Status::Error:
        break;
    case sf::TcpListener::Status::Disconnected:
        break;
    case sf::TcpListener::Status::NotReady:
        break;
    case sf::TcpListener::Status::Partial:
        break;
    }
}

ConnectionManager::ConnectionManager(int listenPort) {
    if(socketListener.listen(listenPort) != sf::TcpListener::Done) {
        LW_LOG(LW_ERROR, "Failed to bind to port: " << listenPort);
    }
    socketListener.setBlocking(false);
}

ConnectionManager::~ConnectionManager() {
    for (std::list<ConnectedNode>::iterator node = connections.begin(); node != connections.end(); ++node) {
        delete node->socket;
    }
}

std::string ConnectionManager::readData() {
    std::string receivedData;
	while(true) {
        poolConnection();
    	std::this_thread::sleep_for(std::chrono::milliseconds(10));
        bool dataReceived = false;
        std::list<std::list<ConnectedNode>::iterator> connectionsToRemove;
		for (std::list<ConnectedNode>::iterator node = connections.begin(); node != connections.end(); ++node) {
			size_t len = 0;
			switch (readData(node->socket, buffer, len)) {
			case sf::TcpSocket::Status::Done: {
				dataReceived = true;
				buffer[len] = '\0';
				receivedData = std::string(buffer);
//				rapidjson::Document doc;
//				doc.Parse(buffer);
//                rapidjson::Value & typeVal = doc["type"];
//                typeVal.
//                if(std::string(typeVal.GetString()) )
//                rapidjson::Value & srcVal = doc["src"];
				break;
			}
			case sf::TcpSocket::Status::Error:
	            LW_LOG(LW_WARN, "Data read error addr:port[name]: data - " << connectionInfo(*node));
				break;
			case sf::TcpSocket::Status::Disconnected:
				LW_LOG(LW_INFO, "Disconnected addr:port[name] - " << connectionInfo(*node));
				connectionsToRemove.push_back(node);
				break;
			case sf::TcpSocket::Status::NotReady:
				break;
			case sf::TcpSocket::Status::Partial:
				break;
			}
			if (dataReceived) {
			    LW_LOG(LW_TRACE, "Data received addr:port[name]: data - " << connectionInfo(*node) << ": " << receivedData);
				return receivedData;
			}
		}
	    for (std::list<std::list<ConnectedNode>::iterator>::iterator rnode = connectionsToRemove.begin(); rnode != connectionsToRemove.end(); ++rnode) {
	        delete (*rnode)->socket;
	        connections.erase(*rnode);
	    }
	}
	return "";
}

sf::TcpSocket::Status ConnectionManager::sendData(sf::TcpSocket* socket, const char* data, size_t len) {
    socket->setBlocking(true);
    return socket->send(data, len);
}

sf::TcpSocket::Status ConnectionManager::readData(sf::TcpSocket* socket, char* data, size_t & len) {
    socket->setBlocking(false);
    return socket->receive(data, BUFFER_SIZE, len);
}

std::string ConnectionManager::connectionInfo(const ConnectedNode & connection) {
    return connection.socket->getRemoteAddress().toString() + ":" + std::to_string(connection.socket->getRemotePort()) + "[" + connection.name + "]";
}

void ConnectionManager::sendData(const std::string & nodeName, const std::string & data) {
    poolConnection();
    std::list<ConnectedNode>::iterator connection = std::find(connections.begin(), connections.end(), ConnectedNode{ nodeName, nullptr });
    if(connection != connections.end()) {
        switch (sendData(connection->socket, data.c_str(), data.size())) {
        case sf::TcpSocket::Status::Done:
            LW_LOG(LW_TRACE, "Data sent addr:port[name]: data - " << connectionInfo(*connection) << ": " << data);
            break;
        case sf::TcpSocket::Status::Error:
            LW_LOG(LW_WARN, "Data sending error addr:port[name]: data - " << connectionInfo(*connection) << ": " << data);
            break;
        case sf::TcpSocket::Status::Disconnected:
            LW_LOG(LW_INFO, "Disconnected addr:port[name] - " << connectionInfo(*connection));
            connections.erase(connection);
            break;
        case sf::TcpSocket::Status::NotReady:
            break;
        case sf::TcpSocket::Status::Partial:
            break;
        }
    }
}
