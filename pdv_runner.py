import socket
import argparse
import netifaces
import json
import subprocess
import os

PDV_RUNNER_PORT = 400
CPP_COMPILER='g++'
C_COMPILER='gcc'
INCLUDE_DIR='.'

counter = 0

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def compile(package):
	filename = package['filename']
	print('Compiling %s' % filename)
	slices = filename.split('.')
	extension = slices[len(slices) - 1]
	compiler = None
	flags = ['-m64', '-Wall']
	if extension == 'c':
		print('This is C file')
		compiler = C_COMPILER
	elif extension == 'cpp' or extension == 'cxx':
		print('This is C++ file')
		compiler = CPP_COMPILER
		flags.append('-std=c++20')
	else:
		print('Error: File extension is not recognized')
		return False
	if not os.path.exists('./.pdv_runner/'):
		os.mkdir('./.pdv_runner')
	disk_filepath = './.pdv_runner/' + filename
	with open(disk_filepath, "w") as file:
		file.write(package['content'])
	args = []
	args.append(compiler)
	args.extend(flags)
	args.append('-I%s/' % INCLUDE_DIR)
	args.append(disk_filepath)
	args.append('-o')
	exec_path = disk_filepath + ".exc"
	args.append(exec_path)
	try:
		result = subprocess.run(args)
	except Exception as error:
		print('Error: Failed to compile ', error)
		return False;
	print(result)
	try:
		result = subprocess.run(exec_path)
	except Exception as error:
		print('Error: Failed to execute ', error)
		return False
	print(result)
	return True

def send_result(s, id):
	try:
		s.sendall("From PDV Runner: Result Available".encode())
	except:
		print('[%d] Failed to send result available notification' % id)
		return
		xml_data = None
	try:
		with open("result.xml", "r") as file:
			xml_data = file.read()
	except:
		print('[%d] Failed to open result.xml file' % id)
		return
	try:
		bytes = xml_data.encode()
		s.sendall(len(bytes).to_bytes(4, byteorder="little"))
		s.sendall(bytes)
	except:
		print('[%d] Failed to send contents of result.xml' % id)
		return
	try:
		print('[%d] Waiting for ack from pdv host' % id)
		buf = recvall(s, len("From PDV Host: ACK"))
	except:
		print('[%d] Failed to receive sck from pdv host' % id)
		return
	if not buf.decode("utf-8") == "From PDV Host: ACK":
		print('[%d] Invalid response from pdv host' % id)
	else:
		print('[%d] PDV host has received the contents of result.xml' % id)
	return

def process(connected_socket, id):
	s = connected_socket
	#try:
	buf = recvall(s, len("From PDV Host: Who are you?"))
	#except:
	#	print('[%d] Failed to receive challenge' % id)
	#	return
	challenge = buf.decode("utf-8")
	if challenge == "From PDV Host: Who are you?":
		response = "I'm PDV Runner".encode()
		try:
			s.sendall(response)
		except:
			print('[%d] Failed to send response' % id)
			return
		try:
			buf = recvall(s, len("From PDV Host: ACK"))
		except:
			print('[%d] Failed to receive ack' % id)
			return
		response = buf.decode("utf-8")
		if response == "From PDV Host: ACK":
			print('[%d] Connection verified' % id)
		try:
			print('[%d] Sending source package request' % id)
			s.sendall("From PDV Runner: Please send file".encode())
		except:
			print('[%d] Failed to send source package request %s' % (id, e))
			return
		try:
			buf = recvall(s, 4)
		except:
			print('[%d] Failed to receive source package length' % id)
			return
		package_len = int.from_bytes(buf, byteorder='little')
		try:
			buf = recvall(s, package_len)
		except:
			print('[%d] Failed to receive source package bytes' % id)
			return
		try:
			print('[%d] Sending ACK')
			s.sendall("From PDV Runner: ACK".encode())
		except:
			print('[%d] Failed to send ACK' % id)
			return
		json_str = buf.decode("utf-8")
		package = json.loads(json_str)
		print(package)
		if compile(package):
			send_result(s, id)
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
		if 'wl' in interface or 'en' in interface or 're' in interface:
			print('Trying to get INET addresses for interface: %s' % interface)
			ip_addresses = try_get_ip_addresses(interface)
			for ip_address in ip_addresses:
				print('\tTrying binding listen socket at IP Address: %s, port: %d' % (ip_address, PDV_RUNNER_PORT), end = ' ')
				try:
					s.bind((ip_address, PDV_RUNNER_PORT))
				except:
					print(' - failed')
					continue
				print(' - success')
				return True
	try:
		print('\tTrying at 127.0.0.1', end = ' ')
		s.bind(("127.0.0.1", PDV_RUNNER_PORT))
	except:
		print(' - failed')
		return False
	print(' - success')
	return True


def main():
	print('PDV Client version 1.0')
	parser = argparse.ArgumentParser(description = 'PDV Client version 1.0')
	parser.add_argument('--port', action = "store", dest = "pdv_port", type=int, required=False)
	parser.add_argument('--cpp_compiler', action="store", dest="cpp_compiler", type=str, required=False)
	parser.add_argument('--c_compiler', action="store", dest="c_compiler", type=str, required=False)
	parser.add_argument('--include_dir', action="store", dest="include_dir", type=str, required=False)
	given_args = parser.parse_args()
	if given_args.cpp_compiler:
		global CPP_COMPILER
		CPP_COMPILER = given_args.cpp_compiler
	if given_args.c_compiler:
		global C_COMPILER
		C_COMPILER = given_args.c_compiler
	if given_args.include_dir:
		global INCLUDE_DIR
		INCLUDE_DIR = given_args.include_dir
	if given_args.pdv_port:
		global PDV_RUNNER_PORT
		PDV_RUNNER_PORT = given_args.pdv_port
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
		print('Listening on port %d ...' % PDV_RUNNER_PORT)
		s.listen(1)
		sk = s.accept()
		id = get_id()
		print('[%d] Connection accepted from %s' % (id, sk[1]))
		process(sk[0], id)
		sk[0].close()
		release_id(id)
	return

main()
