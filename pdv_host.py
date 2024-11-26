import socket
import netifaces
import icmplib
import argparse
import json
import ipaddress
import os
import time

PDV_CLIENT_PORT = 400
# first element is the file name, second element packaged json data to be dispatched to pdv clients
SOURCE_PACKAGE = [str(), bytes()]

def try_get_ip_addresses(interface):
	addrs = []
	address_families = netifaces.ifaddresses(interface)
	if netifaces.AF_INET in address_families:
		ipa_family = address_families[netifaces.AF_INET]
		for ip_addresses in ipa_family:
			if 'addr' in ip_addresses:
				addrs.append(ip_addresses['addr'])
	return addrs

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
		while True:
			try:
				print('Listening for file request')
				buf = s.recv(1024)
			except:
				print('receive error')
				s.close();
				return
			if not buf.decode("utf-8") == "From PDV Client: Please send file":
				print('Invalid request received')
				time.sleep(1.0)
				continue
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
			break
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
	parser.add_argument('--message', action = "store", dest = "message", type=str, required=True)
	given_args = parser.parse_args()
	if given_args.pdv_port:
		global PDV_CLIENT_PORT
		PDV_CLIENT_PORT = given_args.pdv_port
	with open(given_args.file, "r") as file:
		global SOURCE_PACKAGE
		SOURCE_PACKAGE[0] = given_args.file
		filename = os.path.basename(given_args.file)
		content = file.read()
		package = { "filename" : filename, "content" : content }
		json_str = json.dumps(package)
		json_bytes = json_str.encode()
		SOURCE_PACKAGE[1] = json_bytes
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
