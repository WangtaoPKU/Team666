import os;
import socket;
import _thread;
import json;
import argparse;
import hashlib;

parser = argparse.ArgumentParser(prog="server", conflict_handler = "resolve")
host = socket.gethostname();
parser.add_argument("--host", "-h", type = str, default = host, help = "host name (default: socket.gethostname())");
parser.add_argument("--port", "-p", type = int, default = 8080, help = "port number (default: 8080)");
parser.add_argument("--limit", "-l", type = int, default = 10, help = "maximum of clients to serve (default: 10)");
parser.add_argument("--buffer-size", "-b", type = int, default = 1024, help = "buffer size of the receiver (default: 1024)");
parser.add_argument("--path", "-t", type = str, default = "./data/", help = "path of the shared directory (default: ./data/)");
args = parser.parse_args();

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
host = args.host;
port = args.port;
limit = args.limit;
buffer_size = args.buffer_size;
path = args.path;
path_usr = path + "public/";

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
sock.bind((host, port));
print("start a server at", (host, port));
sock.listen(5);

num_conn = 0;

def send_json(msg):
	print("send data to", addr);
	print(str(msg));
	conn.send(json.dumps(msg).encode("utf-8"));

def send_str(msg):
	print("send data to", addr);
	print(msg);
	conn.send(msg.encode("utf-8"));

def send_bytes(msg):
	print("send data to", addr);
	conn.send(msg);

def recv_json(size = buffer_size):
	msg = conn.recv(size);
	print("receive data from", addr);
	msg = msg.decode("utf-8");
	msg = json.loads(msg);
	print(str(msg));
	return msg;

def recv_str(size = buffer_size):
	msg = conn.recv(size);
	print("receive data from", addr);
	msg = msg.decode("utf-8");
	print(msg);
	return msg;

def recv_bytes(size = buffer_size):
	msg = conn.recv(size);
	print("receive data from", addr);
	return msg;

def serve(conn, addr):
	global num_conn;
	print("get connection from", addr);
	while True:
		msg = recv_str();
		try:
			msg = json.loads(msg);
		except:
			print("unrecognized format");
			continue;
		if "command" in msg:
			if msg["command"] == "exit":
				break;
			elif msg["command"] == "download":
				if "data" in msg:
					name = msg["data"];
					name = path_usr + name;
					if os.path.isfile(name):
						with open(name, "rb") as fobj:
							data = fobj.read();
						msg = {
							"response": "ok",
							"size": len(data)
						};
						send_json(msg);
						msg = recv_json();
						if "command" in msg and msg["command"] == "ready":
							send_bytes(data);
					else:
						msg = {
							"response": "not found"
						};
						send_json(msg);
				else:
					msg = {
						"response": "invalid format"
					};
					send_json(msg);
			elif msg["command"] == "upload":
				if "data" in msg and "size" in msg:
					name = msg["data"];
					size = msg["size"];
					name = path_usr + name;
					dirname = os.path.dirname(name);
					if len(dirname) > 0:
						os.makedirs(dirname, exist_ok = True);
					msg = {
						"response": "ok"
					};
					send_json(msg);
					msg = b"";
					while len(msg) < size:
						msg += recv_bytes(size - len(msg));
					with open(name, "wb") as fobj:
						 fobj.write(msg);
				else:
					msg = {
						"response": "invalid format"
					};
					send_json(msg);
			elif msg["command"] == "listdir":
				if "data" in msg:
					name = msg["data"];
					name = path_usr + name;
					if os.path.isdir(name):
						data = os.listdir(name);
						msg = {
							"response": "ok",
							"data": data
						};
						send_json(msg);
					else:
						msg = {
							"response": "not a directory"
						};
						send_json(msg);
				else:
					msg = {
						"response": "invalid format"
					};
					send_json(msg);
	print("disconnnect from", addr);
	conn.close();
	num_conn -= 1;

while num_conn < limit:
	conn, addr = sock.accept();
	num_conn += 1;
	_thread.start_new_thread(serve, (conn, addr));

