#include <iostream>
#include <string>
#include <thread>
#include <SFML/Network.hpp>
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>

void jsonExample(void) {
    const char * json = "{\"val1\":\"str\",\"val2\":3}";
    std::cout << json << std::endl;

    //parse
    rapidjson::Document doc;
    doc.Parse(json);

    //modify
    rapidjson::Value & val1 = doc["val1"];
    val1.SetDouble(1.345);
    rapidjson::Value & val2 = doc["val2"];
    val2.SetInt(val2.GetInt() * 2);

    //serialize
    rapidjson::StringBuffer buffer;
    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
    doc.Accept(writer);

    std::cout << buffer.GetString() << std::endl;
}

int main(int argc, char ** argv) {
    jsonExample();
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