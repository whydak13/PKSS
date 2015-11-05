#ifndef LOGGERWRAPPER_H_
#define LOGGERWRAPPER_H_

#include <string>

#define LW_INIT()           LoggerWrapper::getInstance().init()
#define LW_LVL(lvl)         LoggerWrapper::getInstance().level(lvl)
#define LW_LOG(lvl,msg)     LoggerWrapper::getInstance().log(lvl, (LoggerWrapper::LoggerMessage)msg)

namespace std {
    std::string to_string(std::string string);
}

enum LWLoglevel {
    LW_TRACE,
    LW_DEBUG,
    LW_INFO,
    LW_WARN,
    LW_ERROR
};

class LoggerWrapper {
private:
    LWLoglevel  logLevel;
                LoggerWrapper();

public:
    class LoggerMessage {
    public:
        std::string loggerMessage;

        LoggerMessage(std::string msg) :
            loggerMessage(msg) {}

        template<typename type>
        LoggerMessage & operator <<(type msg) {
            loggerMessage += std::to_string(msg);
            return *this;
        }
    };

    static LoggerWrapper &  getInstance();
    void                    init();
    void                    level(LWLoglevel level);
	void                    log(LWLoglevel level, LoggerMessage toLog);
};

#endif /* LOGGERWRAPPER_H_ */
