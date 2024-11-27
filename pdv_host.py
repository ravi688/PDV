import socket
import netifaces
import icmplib
import argparse
import json
import ipaddress
import os
import time
import subprocess
import MySQLdb
from xml.dom.minidom import parseString

PDV_CLIENT_PORT = 400
# first element is the file name, second element packaged json data to be dispatched to pdv clients
SOURCE_PACKAGE = [str(), bytes()]
TITLE = str()
DESCRIPTION = str()
SOURCE = str()
DB_ENTRY_ID = None

def try_get_ip_addresses(interface):
	addrs = []
	address_families = netifaces.ifaddresses(interface)
	if netifaces.AF_INET in address_families:
		ipa_family = address_families[netifaces.AF_INET]
		for ip_addresses in ipa_family:
			if 'addr' in ip_addresses:
				addrs.append(ip_addresses['addr'])
	return addrs

# receives data of arbitrary length, the length of the data is specified in the first 4 bytes
def receive_file(s):
	buf = None
	try:
		buf = s.recv(4)
	except:
		print('Failed to receive data length')
		return None
	length = int.from_bytes(buf, byteorder="little")
	try:
		buf = s.recv(length)
	except:
		print('Failed to receive data')
		return None
	return buf

def register_entry_db():
	try:
		connection = MySQLdb.connect(host="192.168.1.18", user="pdvhost", passwd="Welcome@123", db="db_pdv")
	except:
		print('Failed to establish connection to mysql database')
		return None
	if not connection:
		print('Connection is null')
		return None
	cursor = connection.cursor()
	query = "INSERT INTO db_pdv.main_table (filename, title, description, source) VALUES (\"%s\",\"%s\",\"%s\",\"%s\");" % (SOURCE_PACKAGE[0], TITLE, DESCRIPTION, SOURCE)
	print(query)
	try:
		cursor.execute(query)
	except:
		print('Failed to insert into db_pdv.main_table')
		connection.close()
		return None
	try:
		cursor.execute("SELECT LAST_INSERT_ID();")
	except:
		connection.close()
		return None
	row = cursor.fetchone()
	entry_id = int(row[0])
	print('entry id: %d' % entry_id)
	query = "CREATE TABLE db_pdv.result_table_%d (id INT AUTO_INCREMENT PRIMARY KEY, chip VARCHAR(255), result TEXT);" % (entry_id)
	print(query)
	try:
		cursor.execute(query)
	except:
		connection.close()
		return None
	try:
		connection.commit()
	except:
		connecion.close()
		return None
	connection.close()
	return entry_id

def register_result_db(xml_result):
	global DB_ENTRY_ID
	if not DB_ENTRY_ID:
		DB_ENTRY_ID = register_entry_db()
		if not DB_ENTRY_ID:
			print('Failed to create database entry')
			return False
	try:
		connection = MySQLdb.connect(host="192.168.1.18", user="pdvhost", passwd="Welcome@123", db="db_pdv")
	except:
		print('Failed to establish connection with mysql database')
		return False
	if not connection:
		return False
	cursor = connection.cursor()
	chip_model = "Chip Model unavailable"
	try:
		document = parseString(xml_result)
		chip_model = str(document.getElementsByTagName('chip')[0].getAttribute('model'))
	except:
		print('Failed to get chip model number, may be xml is invalid?')
	xml_result = xml_result.replace('"', '\\"')
	query = "INSERT INTO db_pdv.result_table_%d (chip, result) VALUES (\"%s\", \"%s\");" % (DB_ENTRY_ID, chip_model, xml_result)
	print(query)
	try:
		cursor.execute(query)
	except:
		connection.close()
		return False
	try:
		connection.commit()
	except:
		connection.close()
		return False
	return True

def check_for_pdv_client(ip_address):
	print(', checking for pdv client at port %d' % PDV_CLIENT_PORT, end = ' ')
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print('- socket error occurred', end = ' ')
		return
	s.setblocking(1)
	s.settimeout(1)
	try:
		s.connect((ip_address, PDV_CLIENT_PORT))
	except socket.error as e:
		s.close()
		print(' - connection error occurred: %s' % e, end = ' ')
		return
	challenge = "From PDV Host: Who are you?"
	try:
		s.sendall(challenge.encode())
	except:
		s.close()
		print(' - send error occurred', end = ' ')
		return
	try:
		buf = s.recv(1024)
	except:
		s.close()
		print(' - recv error ocurred', end = ' ')
		return
	response = buf.decode("utf-8")
	if response == "I'm PDV Client":
		try:
			s.sendall("From PDV Host: ACK".encode())
		except:
			print(' - ack send error', end = ' ')
			s.close()
			return
		print('- found pdv client')
		try:
			print('Listening for file request')
			buf = s.recv(1024)
		except:
			print('receive error')
			s.close();
			return
		if not buf.decode("utf-8") == "From PDV Client: Please send file":
			print('Invalid request received')
			s.close()
			return
		print('Sending file %s' % SOURCE_PACKAGE[0])
		try:
			s.sendall(len(SOURCE_PACKAGE[1]).to_bytes(4, byteorder='little'))
			s.sendall(SOURCE_PACKAGE[1])
		except:
			print('send error')
			s.close()
			return
		try:
			print('Waiting for PDV client ack')
			buf = s.recv(1024)
		except:
			print('failed to receive ack')
			s.close()
			return
		if buf.decode("utf-8") == "From PDV Client: ACK":
			print('PDV client has received file')
		else:
			print('Invalid response received')
		try:
			print('Waiting for PDV client result notification')
			buf = s.recv(1024)
		except:
			print('Failed to get result notification')
			s.close()
			return
		xml_result = None
		if buf.decode("utf-8") == "From PDV Client: Result Available":
			print('Receiving result')
			buf = receive_file(s)
			if buf:
				try:
					s.sendall("From PDV Host: ACK".encode())
				except:
					print('Failed to send result receipt')
					s.close()
					return
			else:
				print('Failed to receive result')
				s.close()
				return
		xml_result = buf.decode("utf-8")
		print(xml_result)
		print('Registering into mysql database...')
		#try:
		register_result_db(xml_result)
		#except:
		#	print('Failed to register into mysql database')
		# Instantiate a thread here for status listening for this pdv client
	else:
		print('- response is wrong')
	s.close()

def ping(ip_address):
	print('\tPinging %s at port %d ..' % (ip_address, PDV_CLIENT_PORT), end = ' ')
	result = icmplib.ping(ip_address, count=1, interval=0.1)
	if result.is_alive:
		print(' - found alive', end = ' ')
		check_for_pdv_client(ip_address)
	print('')

def find_hosts_on_subnet(ip_address):
	packed_addr = socket.inet_aton(ip_address)
	for i in range(0, 256):
		packed_ip_addr = bytes([packed_addr[0], packed_addr[1], packed_addr[2], i])
		unpacked_ip_addr = socket.inet_ntoa(packed_ip_addr)
		ping(unpacked_ip_addr)

def find_hosts():
	for interface in netifaces.interfaces():
		print('Trying to get INET addresses for interface: %s' % interface)
		ip_addresses = try_get_ip_addresses(interface)
		for ip_address in ip_addresses:
			print('\tIP Address: %s' % ip_address)
			if not ip_address == '127.0.0.1':
				print('\tFinding hosts on the same subnet as in %s' % ip_address)
				find_hosts_on_subnet(ip_address)

def is_valid_ip_address(ipa):
	try:
		ip = ipaddress.ip_address(ipa)
	except:
		return False
	return True

def main():
	print('PDV Host version 1.0')
	parser = argparse.ArgumentParser(description = 'PDV Host version 1.0')
	parser.add_argument('--port', action = "store", dest = "pdv_port", type=int, required=False)
	parser.add_argument('--ipa_file', action = "store", dest = "ipa_file", type=str, required=False)
	parser.add_argument('--file', action = "store", dest = "file", type=str, required=True)
	parser.add_argument('--title', action = "store", dest = "title", type=str, required=True)
	parser.add_argument('--description', action = "store", dest = "description", type=str, required=False)
	given_args = parser.parse_args()
	description = given_args.description
	if not given_args.description:
		if not os.path.exists('./pdv_client'):
			os.mkdir('./pdv_client')
		try:
			result = subprocess.call(['nano', '-lm', './pdv_client/description.txt'])
		except SubprocessError as e:
			print('Failed to get description %s' % e)
			return
		is_description = False
		try:
			with open('./pdv_client/description.txt', 'r') as file:
				description = file.read()
		except:
			pass
		finally:
			if not description or len(description) == 0:
				print('Warning: no description is provided')
				description = 'No description provided'
	print('Description: %s' % description)
	global DESCRIPTION
	global TITLE
	global SOURCE
	DESCRIPTION = description.replace('"', '\\"')
	TITLE = given_args.title.replace('"', '\\"')
	if given_args.pdv_port:
		global PDV_CLIENT_PORT
		PDV_CLIENT_PORT = given_args.pdv_port
	with open(given_args.file, "r") as file:
		global SOURCE_PACKAGE
		SOURCE_PACKAGE[0] = given_args.file
		filename = os.path.basename(given_args.file)
		content = file.read()
		SOURCE = content
		package = { "filename" : filename, "content" : content }
		json_str = json.dumps(package)
		json_bytes = json_str.encode()
		SOURCE_PACKAGE[1] = json_bytes
	SOURCE = SOURCE.replace('"', '\\"')
	if given_args.ipa_file:
		file = open(given_args.ipa_file, "r")
		json_str = file.read()
		try:
			json_doc = json.loads(json_str)
		except:
			print('Failed to parse json file: %s' % given_args.ipa_file)
			file.close()
			return
		for key,value in json_doc.items():
			if is_valid_ip_address(value):
				print('Entry %s' % key)
				ping(value)
			else:
				print('Entry %s doesn\'t have valid ip address' % key)
		file.close()
	else:
		find_hosts()
	# wait upon all the instantiated status listening threads here
	return

main()
