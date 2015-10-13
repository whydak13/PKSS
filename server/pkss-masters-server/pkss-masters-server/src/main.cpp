#include <iostream>
#include <string>
#include <thread>
#include <SFML\Network.hpp>

int main(int argc, char ** argv) {
    sf::TcpListener oListener;
    uint8_t aBuffer[1024];
    size_t iSize;
    if (oListener.listen(1234) == sf::TcpListener::Status::Done) {
        sf::TcpSocket oSocket;
        oListener.accept(oSocket);
        oSocket.setBlocking(false);
        while (true) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            sf::TcpSocket::Status oStatus = oSocket.receive(aBuffer, 1024, iSize);
            switch (oStatus) {
            case sf::TcpSocket::Status::Done:
                aBuffer[iSize] = '\0';
                std::cout << aBuffer << std::endl;
                break;
            case sf::TcpSocket::Status::Disconnected:
            case sf::TcpSocket::Status::Error:
                return 0;
            }
        }
    }
    return 0;
}