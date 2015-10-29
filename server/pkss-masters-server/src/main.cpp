#include <iostream>
#include <string>
#include "PKSSServer.h"
#include "easylogging++.h"

INITIALIZE_EASYLOGGINGPP

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


void myCrashHandler(int sig) {
	LOG(INFO) << "Stopping server application";
	// FOLLOWING LINE IS ABSOLUTELY NEEDED AT THE END IN ORDER TO ABORT APPLICATION
	el::Helpers::crashAbort(sig);
}

void sigabrt_handler(int sig) {
	exit(1);
}

int main(int argc, char ** argv) {
	//Handling logger
	el::Configurations conf("../../logs/logger.conf");
	el::Loggers::reconfigureAllLoggers(conf);
	el::Helpers::setCrashHandler(myCrashHandler);
	signal(SIGABRT, sigabrt_handler);

    ConnectionManager manager(1234);
    while (true) {
        manager.readData();
    }
    return 0;
}
