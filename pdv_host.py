import socket
import netifaces
import icmplib
import argparse

PDV_CLIENT_PORT = 234

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
	print('checking for pdv client at port %d' % PDV_CLIENT_PORT, end = ' ')
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print('- socket error occurred', end = ' ')
		return
	s.settimeout(1)
	try:
		s.connect((ip_address, PDV_CLIENT_PORT))
	except:
		print(' - connection error occurred', end = ' ')
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
		print('- found pdv client')
	else:
		print('- response is wrong')

def ping(ip_address):
	print('\tPinging %s ..' % ip_address, end = ' ')
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

def main():
	print('PDV Host version 1.0')
	parser = argparse.ArgumentParser(description = 'PDV Host version 1.0')
	parser.add_argument('--port', action = "store", dest = "pdv_port", type=int, required=False)
	given_args = parser.parse_args()
	PDV_CLIENT_PORT = given_args.pdv_port
	find_hosts()
	return

main()
