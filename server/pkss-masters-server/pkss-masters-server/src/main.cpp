#include <iostream>
#include <string>
#include "PKSSServer.h"

//void jsonExample(void) {
//    const char * json = "{\"val1\":\"str\",\"val2\":3}";
//    std::cout << json << std::endl;
//
//    //parse
//    rapidjson::Document doc;
//    doc.Parse(json);
//
//    //modify
//    rapidjson::Value & val1 = doc["val1"];
//    val1.SetDouble(1.345);
//    rapidjson::Value & val2 = doc["val2"];
//    val2.SetInt(val2.GetInt() * 2);
//
//    //serialize
//    rapidjson::StringBuffer buffer;
//    rapidjson::Writer<rapidjson::StringBuffer> writer(buffer);
//    doc.Accept(writer);
//
//    std::cout << buffer.GetString() << std::endl;
//}

int main(int argc, char ** argv) {
    //PKSSServer server;
    //server.runServer();
    ConnectionManager manager(1234);
    while (true) {
        manager.readData();
    }
    return 0;
}