#ifndef CONNECTIONMANAGER_H
#define CONNECTIONMANAGER_H

#include <string>
#include <exception>
#include <list>

#include <SFML/Network.hpp>

#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>

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

    void                        poolConnection();
    sf::TcpSocket::Status       sendData(sf::TcpSocket * socket, const char * data, size_t len);
    sf::TcpSocket::Status       readData(sf::TcpSocket * socket, char * data, size_t & len);
    std::string                 connectionInfo(const ConnectedNode & connection);

public:
                                ConnectionManager(int listenPort);
                                ~ConnectionManager();
	std::string         		readData();
    void                        sendData(const std::string & nodeName, const std::string & data);
};

#endif /* CONNECTIONMANAGER_H */
