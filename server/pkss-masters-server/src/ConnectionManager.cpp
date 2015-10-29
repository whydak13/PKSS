#include "ConnectionManager.h"
#include "easylogging++.h"
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

sf::TcpSocket * ConnectionManager::findSocket(const std::string & nodeName) {
    if (nodeName != "") {
        ConnectedNode tempNode = { nodeName, nullptr };
        std::list<ConnectedNode>::iterator connection = std::find(connections.begin(), connections.end(), tempNode);
        return connection == connections.end() ? nullptr : connection->socket;
    } else {
        return nullptr;
    }
}

void ConnectionManager::poolConnection() {
    static sf::TcpSocket * newSocket = new sf::TcpSocket;
    switch (socketListener.accept(*newSocket)) {
    case sf::TcpListener::Status::Done: {
        ConnectedNode node { "", newSocket };
		LOG(TRACE) << "Established connection with " << newSocket->getRemoteAddress();
        newSocket->setBlocking(false);
        connections.push_back(node);
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
    socketListener.listen(listenPort);
    socketListener.setBlocking(false);
}

ConnectionManager::~ConnectionManager() {
    for (std::list<ConnectedNode>::iterator node = connections.begin(); node != connections.end(); ++node) {
        delete node->socket;
    }
}

rapidjson::Document ConnectionManager::readData() {
    std::string receivedData;
    while (true) {
        poolConnection();
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        bool dataReceived = false;
        std::list<ConnectedNode>::iterator node = connections.begin();
        while (node != connections.end()) {
            size_t len = 0;
            switch (node->socket->receive(buffer, BUFFER_SIZE, len)) {
            case sf::TcpSocket::Status::Done: {
                dataReceived = true;
                buffer[len] = '\0';
                receivedData = std::string(buffer);
                ++node;
                break;
            }
            case sf::TcpSocket::Status::Error:
                ++node;
                break;
            case sf::TcpSocket::Status::Disconnected:
				LOG(TRACE) << "Disconnected from " << node->socket->getRemoteAddress();
                delete node->socket;
                node = connections.erase(node);
                break;
            case sf::TcpSocket::Status::NotReady:
                ++node;
                break;
            case sf::TcpSocket::Status::Partial:
                ++node;
                break;
            }
            if (dataReceived) {
				LOG(INFO) << receivedData;
                return rapidjson::Document();
            }
        }
    }
}

void ConnectionManager::sendData(const std::string & nodeName, const rapidjson::Document & data) {}
