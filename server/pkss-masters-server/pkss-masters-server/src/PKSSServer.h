#ifndef PKSSSERVER_H
#define PKSSSERVER_H

#include <string>
#include <thread>
#include <vector>
#include <rapidjson/document.h>
#include <rapidjson/writer.h>
#include <rapidjson/stringbuffer.h>

#include "ConnectionManager.h"

class PKSSServer {
public:
            PKSSServer();
            ~PKSSServer();
    void    runServer();
};

#endif /* PKSSSERVER_H */
