import socket
import argparse
import netifaces
import json

PDV_CLIENT_PORT = 400

counter = 0

def process(connected_socket, id):
	s = connected_socket
	try:
		buf = s.recv(1024)
	except:
		print('[%d] Failed to receive challenge' % id)
		return
	challenge = buf.decode("utf-8")
	if challenge == "From PDV Host: Who are you?":
		response = "I'm PDV Client".encode()
		try:
			s.sendall(response)
		except:
			print('[%d] Failed to send response' % id)
			return
		try:
			buf = s.recv(1024)
		except:
			print('[%d] Failed to receive ack' % id)
			return
		response = buf.decode("utf-8")
		if response == "From PDV Host: ACK":
			print('[%d] Connection verified' % id)
		try:
			print('[%d] Sending source package request' % id)
			s.sendall("From PDV Client: Please send file".encode())
		except:
			print('[%d] Failed to send source package request %s' % (id, e))
			return
		try:
			buf = s.recv(4)
		except:
			print('[%d] Failed to receive source package length' % id)
			return
		package_len = int.from_bytes(buf, byteorder='little')
		try:
			buf = s.recv(package_len)
		except:
			print('[%d] Failed to receive source package bytes' % id)
			return
		try:
			print('[%d] Sending ACK')
			s.sendall("From PDV Client: ACK".encode())
		except:
			print('Failed to send ACK')
			return
		json_str = buf.decode("utf-8")
		package = json.loads(json_str)
		print(package)
	else:
		print('[%d] Can\'t solve the challenge' % id)
		return
	return

unreserved_ids = []

def get_id():
	global counter
	id = counter
	if len(unreserved_ids) > 0:
		id = unreserved_ids[len(unreserved_ids) - 1]
		unreserved_ids.remove(id)
	else:
		counter += 1
	return id
def release_id(id):
	unreserved_ids.append(id)
	return

def try_get_ip_addresses(interface):
        addrs = []
        address_families = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in address_families:
                ipa_family = address_families[netifaces.AF_INET]
                for ip_addresses in ipa_family:
                        if 'addr' in ip_addresses:
                                addrs.append(ip_addresses['addr'])
        return addrs

def bind_ip_address(s):
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	for interface in netifaces.interfaces():
		if 'wl' in interface or 'en' in interface:
			print('Trying to get INET addresses for interface: %s' % interface)
			ip_addresses = try_get_ip_addresses(interface)
			for ip_address in ip_addresses:
				print('\tTrying binding listen socket at IP Address: %s, port: %d' % (ip_address, PDV_CLIENT_PORT), end = ' ')
				try:
					s.bind((ip_address, PDV_CLIENT_PORT))
				except:
					print(' - failed')
					continue
				print(' - success')
				return True
	try:
		print('\tTrying at 127.0.0.1', end = ' ')
		s.bind(("127.0.0.1", PDV_CLIENT_PORT))
	except:
		print(' - failed')
		return False
	print(' - success')
	return True


def main():
	print('PDV Client version 1.0')
	parser = argparse.ArgumentParser(description = 'PDV Client version 1.0')
	parser.add_argument('--port', action = "store", dest = "pdv_port", type=int, required=False)
	given_args = parser.parse_args()
	if given_args.pdv_port:
		global PDV_CLIENT_PORT
		PDV_CLIENT_PORT = given_args.pdv_port
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print('Failed to create  socket')
		return
	s.setblocking(1)
	if not bind_ip_address(s):
		s.close()
		print('Failed to bind socket')
		return
	while True:
		print('Listening on port %d ...' % PDV_CLIENT_PORT)
		s.listen(1)
		sk = s.accept()
		id = get_id()
		print('[%d] Connection accepted from %s' % (id, sk[1]))
		process(sk[0], id)
		sk[0].close()
		release_id(id)
	return

main()
