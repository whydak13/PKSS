#ifndef CONNECTIONMANAGER_H
#define CONNECTIONMANAGER_H

#include <string>
#include <exception>
#include <list>

#include <SFML/Network.hpp>

#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>

class ConnectionException : public std::exception {
    std::string message;

public:
    ConnectionException(const std::string & message) {
        this->message = "Connection Exception! : " + message;
    }

    const char* what() const noexcept {
        return this->message.c_str();
    }
};

class CEConnectFailed {

};

class ConnectionManager {
    enum CMConstants { BUFFER_SIZE = 10000 };

    struct ConnectedNode {
        std::string     name;
        sf::TcpSocket * socket;

        bool            operator==(const ConnectedNode & rop) const;
    };

    char                        buffer[BUFFER_SIZE];
    std::list<ConnectedNode>    connections;
    sf::TcpListener             socketListener;

    sf::TcpSocket *             findSocket(const std::string & nodeName);
    void                        poolConnection();

public:
                                ConnectionManager(int listenPort);
                                ~ConnectionManager();
    rapidjson::Document         readData();
    void                        sendData(const std::string & nodeName, const rapidjson::Document & data);
};

#endif /* CONNECTIONMANAGER_H */
