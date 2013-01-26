#!/usr/bin/env python2

import select
import sys
import socket
from time import sleep

import darkcloud.hub.client as client
import darkcloud.hub.request as request
from darkcloud.hub.connectionsocketserver import ConnectionSocketServer
from darkcloud.common.signals import signals

def main_hub():
	server = ConnectionSocketServer()

	signals.connect('connection:connected', client.add)
	signals.connect('connection:disconnected', client.remove)
	signals.connect('connection:data_received', request.parse)

	try:
		while server.pool():
			sleep(0.01)
	except KeyboardInterrupt:
		del server
