#include "LoggerWrapper.h"
#include "easylogging++.h"

INITIALIZE_EASYLOGGINGPP

void myCrashHandler(int sig) {
    LOG(INFO) << "Stopping server application";
    // FOLLOWING LINE IS ABSOLUTELY NEEDED AT THE END IN ORDER TO ABORT APPLICATION
    el::Helpers::crashAbort(sig);
}

void sigabrt_handler(int sig) {
    exit(1);
}

namespace std {
    std::string to_string(std::string string) {
        return string;
    }
}

LoggerWrapper::LoggerWrapper() :
    logLevel(LW_TRACE) {}

LoggerWrapper& LoggerWrapper::getInstance() {
    static LoggerWrapper logger;
    return logger;
}

void LoggerWrapper::level(LWLoglevel level) {
    logLevel = level;
}

void LoggerWrapper::init() {
    //Handling logger
    el::Configurations conf("../../logs/logger.conf");
    el::Loggers::reconfigureAllLoggers(conf);
    el::Helpers::setCrashHandler(myCrashHandler);
    signal(SIGABRT, sigabrt_handler);
}

void LoggerWrapper::log(LWLoglevel level, LoggerMessage toLog) {
    if(level >= logLevel) {
        switch(level) {
            case LW_TRACE:
                LOG(TRACE) << toLog.loggerMessage;
                break;
            case LW_DEBUG:
                LOG(DEBUG) << toLog.loggerMessage;
                break;
            case LW_INFO:
                LOG(INFO) << toLog.loggerMessage;
                break;
            case LW_WARN:
                LOG(WARNING) << toLog.loggerMessage;
                break;
            case LW_ERROR:
                LOG(ERROR) << toLog.loggerMessage;
                break;
        }
    }
}
