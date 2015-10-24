import json

class jsonBuilder(object):
	
	def __init__(self, role):
		self.__dict = {}
		self.__role = role
		self.__init_json = False
		self.switch_to_data_json(role)
		
	def __set_json_type(self, type):
		self.__dict['type'] = type
		
	def __set_json_role(self, role = None):
		if role != None:
			self.__role = role
		self.__dict['src'] = self.__role	
	
	def switch_to_init_json(self, role = None):
		self.__dict.clear()
		self.__init_json = True
		self.__set_json_type('init')
		self.__set_json_role(role)
	
	def switch_to_data_json(self, role = None):
		self.__dict.clear()
		self.__init_json = False
		self.__set_json_type('data')
		self.__set_json_role(role)
	
	def add_field(self, key, value):
		if not self.__init_json:
			self.__dict[key] = value
		
	def serialize(self):
		return json.dumps(self.__dict)
	
	def print_content(self):
		print self.__dict