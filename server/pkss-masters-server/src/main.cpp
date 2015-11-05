#include <iostream>
#include <string>
#include <thread>
#include "PKSSServer.h"
#include "LoggerWrapper.h"


void jsonExample(void) {
    const char * json = "{\"val1\":\"str\",\"val2\":3}";
    LW_LOG(LW_INFO, json);

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

    LW_LOG(LW_INFO, buffer.GetString());
}

int main(int argc, char ** argv) {
    LW_INIT();
	LW_LOG(LW_INFO, "Server up...");

    ConnectionManager manager(2222);
    while (true) {
        std::string data = manager.readData();
    }
    return 0;
}
