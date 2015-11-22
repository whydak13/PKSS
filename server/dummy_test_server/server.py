import logging
import socket
import select
import json

#CLIENT_NAMES = ['wymiennik', 'dostawca', 'budynek1', 'regulator_1', 'gui']
CLIENT_NAMES = ['budynek', 'wymiennik']
TYPE = 'type'
DATA = 'data'
INIT = 'init'
SRC  = 'src'
DELTA = 'trzy_miliony'

def broadcast (server_socket, connection_list, message):
    for socket in connection_list:
        # send the message only to peer
        if socket != server_socket:
            socket.setblocking(True)
            msg = "Global configuration for client %s" % roles_dict[socket]
            logging.debug(msg)
            bytes = socket.sendall(message)
            logging.debug(message)#("Bytes: %d of %d" %(bytes, len(message))) +
            socket.setblocking(False)

def remove_socket(socket_to_remove, connection_list, roles_dict):
    msg = "Client %s disconnected." % socket_to_remove.getsockname()[0]
    if roles_dict[socket_to_remove] !="":
        msg += " Role: %s" % roles_dict[socket_to_remove]
    logging.debug(msg)
    socket_to_remove.close()
    connection_list.remove(socket_to_remove)
    del roles_dict[socket_to_remove]
    
def prepare_client_iteration_activity(client_iteration_activity, roles_dict):
    client_iteration_activity.clear()
    for value in roles_dict.values():
        client_iteration_activity[value] = True
        
def is_iteration_done(client_iteration_activity, roles_dict):
    is_done = False
    for value in roles_dict.values():
        is_done = is_done or client_iteration_activity[value]
    is_done = not is_done
    logging.debug('Is iteration done %s' % str(is_done))
    return is_done

def merge_with_global_json(data_json, broadcast_msg):
    logging.debug('Merging Jsons')
    common = set(data_json.keys()).intersection(broadcast_msg.keys())
    if common:
        msg = 'New data json overrides keys from global json %s' % str(common) 
        logging.info(msg)
    broadcast_msg.update(data_json)   

def process_initialization_json(init_json, init_sock, roles_dict, connection_list):
    logging.debug(init_json)
    if init_json[TYPE] != INIT or init_json.get(SRC) == None:
        logging.debug("Client %s wrong init" % init_sock.getsockname()[0])
        remove_socket(init_sock, connection_list, roles_dict)
    else:
        role = init_json[SRC]
        if role not in CLIENT_NAMES:
            logging.debug("Client %s reported wrong role" % init_sock.getsockname()[0])
            remove_socket(init_sock, connection_list, roles_dict)
        else:
            if role not in roles_dict.values():
                roles_dict[init_sock] = role
                msg = "Client %s ok init. " % init_sock.getsockname()[0]
                logging.debug(msg +  "New role taken: %s" % role)
                logging.debug("Actual client list: " + '[%s]' % ' '.join(map(str, roles_dict.values())))
            else:
                logging.debug("Client %s reported busy role" % init_sock.getsockname()[0])
                remove_socket(init_sock, connection_list, roles_dict)

def process_data_json(data_json, data_sock, roles_dict, broadcast_msg):
    logging.debug(data_json)
    if data_json[TYPE] != DATA or data_json.get(SRC) == None:
        logging.debug("Client %s wrong data header" % roles_dict[data_sock])
        return True
    else:
        role = data_json[SRC]
        if role != roles_dict[data_sock]:
            msg = "Role was changed in data json %s -> %s" % (roles_dict[data_sock], role)
            logging.debug(msg)
            return True
        else:
            del data_json[TYPE]
            del data_json[SRC]
            merge_with_global_json(data_json, broadcast_msg)
            return False

def add_time(broadcast_msg, delta_value):
    broadcast_msg[DELTA] = delta_value

if __name__ == "__main__":
    
    logging.basicConfig(format = '%(levelname)s %(filename)s: %(message)s', level = logging.DEBUG)
    delta_value = 10000

    CONNECTION_LIST = []
    RECV_BUFFER = 4096
    HOST, PORT = "localhost", 1234
         
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
 
    # Add server socket to the list of readable connections
    CONNECTION_LIST.append(server_socket)
    logging.info("Server started on port " + str(PORT))

    initialized = False
    iteration = 0
    roles_dict = {}
    client_iteration_activity = {}
    broadcast_msg = {}
    
    while True:
        read_sockets,write_sockets,error_sockets = select.select(CONNECTION_LIST,[],[], 1.0)
        for sock in read_sockets:           
            #New connection
            if sock == server_socket:
                sock.setblocking(False)
                sockfd, addr = server_socket.accept()
                roles_dict[sockfd] = ""
                CONNECTION_LIST.append(sockfd)
                logging.debug("Client %s connected" % sockfd.getsockname()[0])
            else:
                #Initialization
                if not initialized and roles_dict[sock] == "":
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        try:
                            init_json = json.loads(data)
                            process_initialization_json(init_json, sock, roles_dict, CONNECTION_LIST)
                        except ValueError:
                            logging.debug('Init string from %s is not Json' % sock.getsockname()[0])
                            logging.debug(str(data))
                    else:
                        remove_socket(sock, CONNECTION_LIST, roles_dict)
                
                #Normal
                if initialized and client_iteration_activity[roles_dict[sock]]:
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        try:
                            data_json = json.loads(data)
                            is_processed = process_data_json(json.loads(data), sock, roles_dict, broadcast_msg)
                            client_iteration_activity[roles_dict[sock]] = is_processed
                        except ValueError:
                            logging.debug('Data string from %s is not Json' % str(roles_dict[sock]))
                            logging.debug(str(data))
                    else:
                        remove_socket(sock, CONNECTION_LIST, roles_dict)

        # Init phase done
        if initialized==False and set(roles_dict.values()) == set(CLIENT_NAMES):
            initialized = True
            iteration += 1
            prepare_client_iteration_activity(client_iteration_activity, roles_dict)
            broadcast_msg[TYPE] = INIT
            add_time(broadcast_msg, delta_value)
            delta_value = delta_value + 1
            broadcast(server_socket, CONNECTION_LIST, json.dumps(broadcast_msg))
            logging.info("Initialization completed successfully")
        
        # Iteration transition
        if initialized==True:
            all_connected = set(roles_dict.values()) == set(CLIENT_NAMES)
            if all_connected and is_iteration_done(client_iteration_activity, roles_dict):
                broadcast_msg[TYPE] = DATA
                add_time(broadcast_msg, delta_value)
                delta_value = delta_value + 1
                broadcast(server_socket, CONNECTION_LIST, json.dumps(broadcast_msg))
                client_iteration_activity.clear()
                prepare_client_iteration_activity(client_iteration_activity, roles_dict)
                broadcast_msg.clear()
                logging.info("Start of iteration %s" % str(iteration))
                iteration += 1
         
    server_socket.close()
