from time import sleep

import darkcloud.hub.client as client
from darkcloud.hub.request import RequestServer
from darkcloud.hub.connectionsocketserver import ConnectionSocketServer
from darkcloud.common.signals import signals

def main():
	server = ConnectionSocketServer()
	request = RequestServer()

	signals.connect('connection:connected', client.add)
	signals.connect('connection:disconnected', client.remove)
	signals.connect('connection:data_received', request.parse)

	try:
		while server.pool():
			sleep(0.01)
	except KeyboardInterrupt:
		pass

	del server
