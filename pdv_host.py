import socket
import netifaces

def try_get_ip_addresses(interface):
	addrs = []
	address_families = netifaces.ifaddresses(interface)
	if netifaces.AF_INET in address_families:
		ipa_family = address_families[netifaces.AF_INET]
		for ip_addresses in ipa_family:
			if 'addr' in ip_addresses:
				addrs.append(ip_addresses['addr'])
	return addrs

def ping(ip_address):
	print('\tPinging %s ..' % ip_address)
	return True

def find_hosts_on_subnet(ip_address):
	hosts = [ip_address]
	packed_addr = socket.inet_aton(ip_address)
	for i in range(0, 256):
		packed_ip_addr = bytes([packed_addr[0], packed_addr[1], packed_addr[2], i])
		unpacked_ip_addr = socket.inet_ntoa(packed_ip_addr)
		result = ping(unpacked_ip_addr)
		if result:
			hosts.append(unpacked_ip_addr)
	return hosts

def find_hosts():
	hosts = []
	for interface in netifaces.interfaces():
		print('Trying to get INET addresses for interface: %s' % interface)
		ip_addresses = try_get_ip_addresses(interface)
		for ip_address in ip_addresses:
			print('\tIP Address: %s' % ip_address)
			if not ip_address == '127.0.0.1':
				print('\tFinding hosts on the same subnet as in %s' % ip_address)
				network_hosts = find_hosts_on_subnet(ip_address)
				hosts.extend(network_hosts)
	return hosts

def main():
	print('PDV Host version 1.0')
	ipa_list = find_hosts()
#	for ipa in ipa_list:
#		print('IP Address: %s' % ipa)
	if len(ipa_list) == 0:
		print('No hosts found')
	return

main()
