import readline
import sys
from socket import gethostbyaddr

from darkcloud.common.connectionsocketclient import ConnectionSocketClient
from darkcloud.common.signals import signals

import darkcloud.settings as settings

def main():
	settings.DEBUG = False

	client = ConnectionSocketClient()
	if client == False:
		sys.exit(1)

	client.connect()

	x = client.remote_addr().split(':')
	remote = '%s:%s' % (gethostbyaddr(x[0])[0], x[1])

	try:
		client.send("auth adm admin 1234\n");
		print client.pool()
		cmd = ''
		while True:
			cmd = raw_input('\033[0;33m-(\033[1;33m%s\033[0;33m)->\033[0m ' % remote)
			if cmd == 'quit':
				raise EOFError

			client.send(cmd);
			print client.pool()
	except KeyboardInterrupt:
		pass
	except EOFError:
		pass
	
	print("\nQuitting...")
	
	client.disconnect()
	
	del client
