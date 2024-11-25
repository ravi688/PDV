import socket
import argparse

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
	s.bind(("192.168.1.20", PDV_CLIENT_PORT))
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
