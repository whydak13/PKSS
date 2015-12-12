import socket
import time
import json
import sys
import os

sys.path.append(os.path.join(os.path.realpath(__file__), '..'))

from json_builder import jsonBuilder

ROLE = 'budynek'

CISNIENIE = 'cisnienie'

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
    cisnienie = 1000
    json_builder.add_field(CISNIENIE, cisnienie)

    #json_builder.print_content()

    try:
        while(True):
            data = my_socket.recv(RECV_BUFFER)
            print "RECEIVED: " + data
            time.sleep(3)
            cisnienie -= 1
            json_builder.add_field(CISNIENIE, cisnienie)
            data_sent = json_builder.serialize()
            my_socket.send(data_sent)
            print "SENT: " + data_sent 
    except KeyboardInterrupt:
        my_socket.shutdown(socket.SHUT_RDWR)
        my_socket.close()