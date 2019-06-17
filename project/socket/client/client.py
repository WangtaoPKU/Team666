import os;
import socket;
import _thread;
import json;
import argparse;
import time;
import wx;

parser = argparse.ArgumentParser(prog="client", conflict_handler = "resolve");
host = socket.gethostname();
parser.add_argument("--host", "-h", type = str, default = host, help = "host name (default: socket.gethostname())");
parser.add_argument("--port", "-p", type = int, default = 8080, help = "port number (default: 8080)");
parser.add_argument("--buffer-size", "-b", type = int, default = 1024, help = "buffer size of the receiver (default: 1024)");
parser.add_argument("--path", "-t", type = str, default = "./data/", help = "path of the download directory (default: ./data/)");
args = parser.parse_args();

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
host = args.host;
port = args.port;
buffer_size = args.buffer_size;
path = args.path;

class client_app(wx.App):

	#overload the initializer
	def OnInit(self):
		sock.connect((host, port));
		print("connect to", (host, port));
		self.init_frame();
		return True;

	#overload the destructor
	def OnExit(self):
		msg = {
			"command": "exit"
		};
		msg = json.dumps(msg);
		sock.sendall(msg.encode("utf-8"));
		sock.close();
		print("disconnect from", (host, port));
		return True;

	#initialize the frame
	def init_frame(self):

		#create a frame
		self.frame = wx.Frame();
		self.frame.Create(None, wx.ID_ANY, "Client");
		font_text = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName = "consolas");
		self.frame.SetFont(font_text);
		font_index = wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName = "consolas");
		self.frame.SetFont(font_index);

		#create background elements
		sizer_base = wx.BoxSizer(wx.HORIZONTAL);
		self.frame.SetSizer(sizer_base);
		panel_base = wx.Panel(self.frame);
		panel_base.SetBackgroundColour(wx.BLACK);
		sizer_base.Add(panel_base, 1, wx.ALL | wx.EXPAND,5);
		sizer_main = wx.BoxSizer(wx.HORIZONTAL);
		panel_base.SetSizer(sizer_main);

		#create a notebook on the left
		sizer_dir = wx.BoxSizer(wx.VERTICAL);
		sizer_main.Add(sizer_dir, 1, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND, 5);
		book_tree = wx.Notebook(panel_base, size = wx.Size(600,400), style = wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL);
		sizer_dir.Add(book_tree, 1, wx.ALL | wx.EXPAND, 5);
		book_tree.SetFont(font_index);

		self.tree_server = wx.TreeCtrl(book_tree);
		book_tree.AddPage(self.tree_server, "server");
		self.tree_server.SetForegroundColour(wx.Colour(200,200,200));
		self.tree_server.SetBackgroundColour(wx.Colour(32,32,32));
		font_text = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName = "consolas");
		self.tree_server.SetFont(font_text);
		self.tree_server.AddRoot(".", data = (".", False));
		self.tree_server.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_tree_server_item_select);

		self.tree_client = wx.TreeCtrl(book_tree);
		book_tree.AddPage(self.tree_client, "client");
		self.tree_client.SetForegroundColour(wx.Colour(200,200,200));
		self.tree_client.SetBackgroundColour(wx.Colour(32,32,32));
		font_text = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, faceName = "consolas");
		self.tree_client.SetFont(font_text);
		self.tree_client.AddRoot(".", data = (".", False));
		self.tree_client.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_tree_client_item_select);

		#create a notebook on the right
		sizer_book = wx.BoxSizer(wx.VERTICAL);
		sizer_main.Add(sizer_book, 1, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND, 5);
		self.notebook = wx.Notebook(panel_base, size = wx.Size(600,400), style = wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL);
		sizer_book.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 5);
		self.notebook.SetFont(font_index);

		#add page interaction to the notebook
		self.panel_inter = wx.Panel(self.notebook, style = wx.TAB_TRAVERSAL);
		self.notebook.AddPage(self.panel_inter, "interaction");
		self.panel_inter.SetForegroundColour(wx.Colour(200,200,200));
		self.panel_inter.SetBackgroundColour(wx.Colour(32,32,32));
		self.panel_inter.SetFont(font_text);
		sizer_inter_base = wx.BoxSizer(wx.VERTICAL);
		sizer_inter = wx.BoxSizer(wx.VERTICAL);
		self.panel_inter.SetSizer(sizer_inter);

		#add a text control to send message
		label_send = wx.StaticText(self.panel_inter, label = "send message to the server");
		label_send.SetForegroundColour(wx.Colour(200,200,200));
		label_send.SetFont(font_text);
		sizer_inter.Add(label_send, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		sizer_send = wx.BoxSizer(wx.HORIZONTAL);
		sizer_inter.Add(sizer_send, 0, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND, 5);
		self.text_msg = wx.TextCtrl(self.panel_inter, style = wx.TE_PROCESS_ENTER);
		sizer_send.Add(self.text_msg, 1, wx.ALL | wx.ALIGN_CENTER, 5);
		self.text_msg.SetForegroundColour(wx.Colour(200,200,200));
		self.text_msg.SetBackgroundColour(wx.Colour(32,32,32));
		self.text_msg.SetFont(font_text);
		self.button_send = wx.Button(
			self.panel_inter, label = "send", size = (100, 40)
		);
		self.button_send.SetFont(font_text);
		self.button_send.SetForegroundColour(wx.Colour(200,200,200));
		self.button_send.SetBackgroundColour(wx.Colour(0,0,0));
		sizer_send.Add(self.button_send, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		self.button_send.Bind(wx.EVT_BUTTON, self.on_send);

		#add text controls to transfer files
		label_file = wx.StaticText(self.panel_inter, label = "file transmission");
		label_file.SetForegroundColour(wx.Colour(200,200,200));
		label_file.SetFont(font_text);
		sizer_inter.Add(label_file, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		sizer_server = wx.BoxSizer(wx.HORIZONTAL);
		sizer_inter.Add(sizer_server, 0, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND, 5);
		label_server = wx.StaticText(self.panel_inter, label = "server:");
		label_server.SetForegroundColour(wx.Colour(200,200,200));
		label_server.SetFont(font_text);
		sizer_server.Add(label_server, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		self.text_server = wx.TextCtrl(self.panel_inter, style = wx.TE_PROCESS_ENTER);
		sizer_server.Add(self.text_server, 1, wx.ALL | wx.ALIGN_CENTER, 5);
		self.text_server.SetForegroundColour(wx.Colour(200,200,200));
		self.text_server.SetBackgroundColour(wx.Colour(32,32,32));
		self.text_server.SetFont(font_text);

		sizer_client = wx.BoxSizer(wx.HORIZONTAL);
		sizer_inter.Add(sizer_client, 0, wx.ALL | wx.ALIGN_CENTER | wx.EXPAND, 5);
		label_client = wx.StaticText(self.panel_inter, label = "client:");
		label_client.SetForegroundColour(wx.Colour(200,200,200));
		label_client.SetFont(font_text);
		sizer_client.Add(label_client, 0, wx.ALL | wx.ALIGN_CENTER, 5);

		self.text_client = wx.TextCtrl(self.panel_inter, style = wx.TE_PROCESS_ENTER);
		sizer_client.Add(self.text_client, 1, wx.ALL | wx.ALIGN_CENTER, 5);
		self.text_client.SetForegroundColour(wx.Colour(200,200,200));
		self.text_client.SetBackgroundColour(wx.Colour(32,32,32));
		self.text_client.SetFont(font_text);

		sizer_file = wx.BoxSizer(wx.HORIZONTAL);
		sizer_inter.Add(sizer_file, 0, wx.ALL | wx.ALIGN_CENTER, 5);
		self.button_download = wx.Button(
			self.panel_inter, label = "download", size = (200, 40)
		);
		self.button_download.SetFont(font_text);
		self.button_download.SetForegroundColour(wx.Colour(200,200,200));
		self.button_download.SetBackgroundColour(wx.Colour(0,0,0));
		sizer_file.Add(self.button_download, 1, wx.ALL | wx.ALIGN_CENTER, 5);
		self.button_download.Bind(wx.EVT_BUTTON, self.on_download);

		self.button_upload = wx.Button(
			self.panel_inter, label = "upload", size = (200, 40)
		);
		self.button_upload.SetFont(font_text);
		self.button_upload.SetForegroundColour(wx.Colour(200,200,200));
		self.button_upload.SetBackgroundColour(wx.Colour(0,0,0));
		sizer_file.Add(self.button_upload, 1, wx.ALL | wx.ALIGN_CENTER, 5);
		self.button_upload.Bind(wx.EVT_BUTTON, self.on_upload);

		#add page dir to the notebook
		self.text_dir = wx.TextCtrl(self.notebook, style = wx.TE_MULTILINE | wx.TE_READONLY);
		self.notebook.AddPage(self.text_dir, "directory");
		self.text_dir.SetForegroundColour(wx.Colour(200,200,200));
		self.text_dir.SetBackgroundColour(wx.Colour(32,32,32));
		self.text_dir.SetFont(font_text);

		#add page log to the notebook
		self.text_log = wx.TextCtrl(self.notebook, style = wx.TE_MULTILINE | wx.TE_READONLY);
		self.notebook.AddPage(self.text_log, "log");
		self.text_log.SetForegroundColour(wx.Colour(200,200,200));
		self.text_log.SetBackgroundColour(wx.Colour(32,32,32));
		self.text_log.SetFont(font_text);

		#set the suitable size of the frame
		sizer_base.SetSizeHints(self.frame);

		#show the frame
		self.frame.Show(True);

	def print_log(self, info):
		self.text_log.AppendText(info);

	def send_json(self, msg):
		self.print_log("send data to (%s, %d)\n" % (host, port));
		self.print_log(str(msg) + "\n");
		sock.sendall(json.dumps(msg).encode("utf-8"));

	def send_str(self, msg):
		self.print_log("send data to (%s, %d)\n" % (host, port));
		self.print_log(msg + "\n");
		sock.sendall(msg.encode("utf-8"));

	def send_bytes(self, msg):
		self.print_log("send data to (%s, %d)\n" % (host, port));
		#self.print_log(msg + "\n");
		sock.sendall(msg);

	def recv_json(self, size = buffer_size):
		msg = sock.recv(size);
		self.print_log("receive data from (%s, %d)\n" % (host, port));
		msg = msg.decode("utf-8");
		msg = json.loads(msg);
		self.print_log(str(msg) + "\n");
		return msg;

	def recv_str(self, size = buffer_size):
		msg = sock.recv(size);
		self.print_log("receive data from (%s, %d)\n" % (host, port));
		msg = msg.decode("utf-8");
		self.print_log(msg + "\n");
		return msg;

	def recv_bytes(self, size = buffer_size):
		msg = sock.recv(size);
		self.print_log("receive data from (%s, %d)\n" % (host, port));
		return msg;

	def on_send(self, event):
		msg = self.text_msg.GetValue();
		self.send_str(msg);

	def on_download(self, event):
		msg = {
			"command": "download",
			"data": self.text_server.GetValue()
		};
		self.send_json(msg);
		msg = self.recv_json();
		if "response" in msg and msg["response"] == "ok":
			size = msg["size"];
			msg = {"command": "ready"}
			self.send_json(msg);
			msg = b""
			while len(msg) < size:
				msg += self.recv_bytes(size - len(msg));
			name = self.text_client.GetValue();
			name = path + name;
			dirname = os.path.dirname(name);
			if len(dirname) > 0:
				os.makedirs(dirname, exist_ok = True);
			with open(name, "wb") as fobj:
				fobj.write(msg);

	def on_upload(self, event):
		name = self.text_client.GetValue();
		name = path + name;
		if not os.path.isfile(name):
			log_print("file not found");
			return;
		with open(name, "rb") as fobj:
			data = fobj.read();
		name = self.text_server.GetValue();
		msg = {
			"command": "upload",
			"data": name,
			"size": len(data)
		};
		self.send_json(msg);
		msg = self.recv_json();
		if "response" in msg and msg["response"] == "ok":
			self.send_bytes(data);

	def on_tree_server_item_select(self, event):
		item = event.GetItem();
		name, flag = self.tree_server.GetItemData(item);
		if flag:
			self.tree_server.DeleteChildren(item);
		msg = {
			"command": "listdir",
			"data": name
		}
		self.send_json(msg);
		msg = self.recv_json();
		if "response" in msg and msg["response"] == "ok" and "data" in msg:
			data = msg["data"];
			for p in data:
				self.tree_server.AppendItem(item, p, data = (name + "/" + p, False));
			self.tree_server.SetItemData(item, (name, True));
		self.text_server.SetValue(name);

	def on_tree_client_item_select(self, event):
		item = event.GetItem();
		name, flag = self.tree_client.GetItemData(item);
		if flag:
			self.tree_client.DeleteChildren(item);
		if os.path.isdir(path + name):
			data = os.listdir(path + name);
			for p in data:
				self.tree_client.AppendItem(item, p, data = (name + "/" + p, False));
			self.tree_client.SetItemData(item, (name, True));
		self.text_client.SetValue(name);

if __name__ == "__main__":
	app = client_app(False);
	app.MainLoop();
