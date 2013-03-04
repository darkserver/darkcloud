from time import sleep
import sys

from darkcloud.common.connectionsocketclient import ConnectionSocketClient
from darkcloud.common.signals import signals

import darkcloud.settings as settings

def main():
	settings.DEBUG = False

	client = ConnectionSocketClient()
	if client == False:
		sys.exit(1)

	client.connect()

	try:
		client.send("auth adm admin 1234\n");
		print client.pool()
		cmd = ''
		while True:
			cmd = raw_input('\033[0;33m-(\033[1;33m%s\033[0;33m)->\033[1;32m ' % settings.HUB_HOST)
			if cmd == 'quit':
				break
			sys.stdout.write('\033[0m')
			client.send(cmd);
			print client.pool()
	except KeyboardInterrupt:
		pass
	
	client.disconnect()
	
	del client
