import socket
import Queue
from time import sleep

from darkcloud.common.connectionsocket import ConnectionSocket
from darkcloud.common.hmac import HMAC
from darkcloud.common.signals import signals

import darkcloud.settings as settings

class ConnectionSocketClient(ConnectionSocket):
	def __init__(self):
		if not settings.HUB_HOST or not settings.HUB_PORT:
			print("Connection details not specified.\n");
			print("You must specify HUB_HOST and HUB_PORT in your settings file\n");
			print("And it must point to DarkCloud Hub server\n");
			return False

		ConnectionSocket.__init__(self)

		self.connected = None
		self.data = None

	def __del__(self):
		self.socket.close()
	
	def connect(self):
		try:
			if self.connected == False:
				sleep(5)

			self.socket.connect((settings.HUB_HOST, settings.HUB_PORT))

			if self.socket:
				self.connected = True
		except socket.error as err:
			if self.connected or self.connected == None:
				print("\033[1;31mCan't connect to %s:%s\033[0m: %s" % (settings.HUB_HOST, settings.HUB_HOST, err[1]))
				self.connected = False
				signals.emit('connection:disconnected', False)
	
	def disconnect(self):
		self.close()

	def send(self, data):
		hmac = HMAC()
		signed_message = hmac.sign_message("", "", data)
		ConnectionSocket.send(self, signed_message)
	
	def lost(self, err):
		print("\033[1;31mConnection to %s:%s lost\033[0m: %s" % (settings.HUB_HOST, settings.HUB_PORT, err))
		signals.emit('connection:lost')
		self.connected = False
		self.connect()

	def pool(self):
		try:
			if self.socket:
				signals.emit('connection:data_received', self.socket, self.data)

				self.data = self.socket.recv(settings.BUFFER_SIZE).rstrip('\n')
			else:
				if self.connected or self.connected == None:
					print("Not connected. Connecting. Autoreconnect every 5 second")
				self.connect()
		except socket.error as err:
			self.lost(err)

		return self.data
