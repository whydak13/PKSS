import socket
import time
import json
import sys
import os
import random

sys.path.append(os.path.join(os.path.realpath(__file__), '..'))

from json_builder import jsonBuilder

ROLE = 'wymiennik'
T_o = 'T_o'
T_zm = 'T_zm'
T_zco2 = 'T_pcob2'
F_cob2 = 'F_cob2'
T_r2 = 'T_r2'
U_b2 = 'U_b2'

RAND_BASE = 100


TEMPERATURA = 'temperatura'

if __name__ == '__main__':
    host = "192.168.1.103"
    port = 1234
    RECV_BUFFER = 4096

    json_builder = jsonBuilder(ROLE)
    json_builder.switch_to_init_json()

    #json_builder.print_content()

    my_socket = socket.create_connection((host, port), 2)
    my_socket.setblocking(True)
    init_data = json_builder.serialize()
    my_socket.send(init_data)
    print "SENT: " + init_data
    time.sleep(1)

    json_builder.switch_to_data_json()
    temp = 32
    #json_builder.add_field(TEMPERATURA, temp)

    #json_builder.print_content()

    try:
        while(True):
            data = my_socket.recv(RECV_BUFFER)
            print "RECEIVED: " + data
            time.sleep(1)
            temp += 1
            #json_builder.add_field(TEMPERATURA, temp)
            json_builder.add_field(T_o, random.randint(1,RAND_BASE)/10 - 10)
            json_builder.add_field(T_zm, random.randint(1,RAND_BASE))
            json_builder.add_field(T_zco2, random.randint(1,RAND_BASE))
            json_builder.add_field(F_cob2, random.randint(1,RAND_BASE))
            json_builder.add_field(T_r2, random.randint(1,RAND_BASE))
            json_builder.add_field(U_b2, random.random())
            data_sent = json_builder.serialize()
            my_socket.send(data_sent)
            print "SENT: " + data_sent 
    except KeyboardInterrupt:
        my_socket.shutdown(socket.SHUT_RDWR)
        my_socket.close()
