import darkcloud.hub.client as client

def parse(connection, message):
	addr = connection.remote_addr()
	print("%-21s | \033[0;33m%-12s\033[0m | %s" % (addr, client.get_by_addr(addr), message))
	data = message.strip().split(' ')
	try:
		isauth, cl = client.authorized(addr)

		if not isauth:
			if data[0] == 'auth':
				if client.auth(addr, data[1], data[2], data[3]):
					connection.send('ok darkcloud 0.1')
					return
				else:
					connection.send('fail')
					return
			else:
				connection.send('access denied\n')
				return

		elif isauth == client.CLIENT_ADMIN:
			if data[0] == 'list':
				if len(data) > 1:
					if data[1]:
						connection.send(client.list_all([data[1]]))
						return
				else:
					connection.send(client.list_all())
					return

		elif isauth == client.CLIENT_SERVER:
			if data[0] == 'get':
				if data[1] == 'config':
					return
			connection.send('no actions')
			return

	except IndexError:
		pass

	connection.send('request invalid')
