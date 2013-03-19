import sys
from time import sleep
from socket import gethostbyaddr

from darkcloud.hub.request import Request
from darkcloud.common.connectionsocketclient import ConnectionSocketClient
from darkcloud.common.signals import signals

import darkcloud.settings as settings

def on_connect(client):
	client.send("auth slave %s imslave!\n" % (gethostbyaddr('127.0.0.1')[0]))
	print client.pool()

def main():
	client = ConnectionSocketClient()
	request = Request()

	if client == False:
		sys.exit(1)
	
	signals.connect('connection:connected', on_connect)
	signals.connect('connection:data_received', request.parse)
	
	client.connect()

	try:
		while True:
			client.pool()
	except KeyboardInterrupt:
		pass
	
	client.disconnect()
	
	del client
