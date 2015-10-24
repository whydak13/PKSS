import socket
import time
import json
import sys
import os

sys.path.append(os.path.join(os.path.realpath(__file__), '..'))

from json_builder import jsonBuilder

ROLE = 'wymiennik'

if __name__ == '__main__':
	host = '192.168.1.111'
	port = 1234
	
	json_builder = jsonBuilder(ROLE)
	json_builder.switch_to_init_json()
	
	json_builder.print_content()

	my_socket = socket.create_connection((host, port), 2)
	my_socket.send(json_builder.serialize())
	time.sleep(1)
	
	json_builder.switch_to_data_json()
	json_builder.add_field('temperatura', 32.5)
	
	json_builder.print_content()
	
	try:
		while(True):
			my_socket.send(json_builder.serialize())
			time.sleep(2)
	except KeyboardInterrupt:
		my_socket.shutdown(socket.SHUT_RDWR)
