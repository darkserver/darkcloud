CLIENT_UNKNOWN = 0
CLIENT_ADMIN = 1
CLIENT_SERVER = 2

clients = []

def add(connection):
	clients.append({
		'conn' : connection,
		'address' : connection.remote_addr(),
		'type' : CLIENT_UNKNOWN,
	})

	return True

def modify(addr, data):
	for c in clients:
		if c['address'] == addr:
			for k,v in data.items():
				c[k] = v
			return True

	return False

def remove(addr):
	try:
		for c in clients:
			if c['address'] == addr:
				if c['type'] == CLIENT_ADMIN:
					print("\033[1;33madmin removed [%s from %s]\033[0m" % (c['username'], c['address']))
				elif c['type'] == CLIENT_SERVER:
					print("\033[1;32madmin removed [%s from %s]\033[0m" % (c['hostname'], c['address']))
				clients.remove(c)
	except ValueError:
		pass

def list_all(show = ['admins', 'slaves']):
	out = {}

	if 'admins' in show:
		out['admins'] = []
		for c in clients:
			if c['type'] == CLIENT_ADMIN:
				out['admins'].append(c.copy())
		for x in out['admins']:
			x.pop('conn')

	if 'slaves' in show:
		out['slaves'] = []
		for c in clients:
			if c['type'] == CLIENT_SERVER:
				out['slaves'].append(c.copy())
		for x in out['slaves']:
			x.pop('conn')
	
	return out

def auth(addr, client_type, clientname, password):
	if client_type == "adm":
		if clientname == "admin" and password == "1234":
			return modify(addr, {
				'type'     : CLIENT_ADMIN,
				'address'  : addr,
				'username' : clientname,
			})

	elif client_type == "slave":
		if password == "imslave!":
			return modify(addr, {
				'type'     : CLIENT_SERVER,
				'address'  : addr,
				'hostname' : clientname,
			})

	return False

def authorized(addr):
	for c in clients:
		if addr == c['address']:
			return (c['type'], c)

	return (False, None)

def get_by_addr(addr):
	for c in clients:
		if addr == c['address']:
			if 'username' in c:
				return c['username']
			elif 'hostname' in c:
				return c['hostname']

	return '-unknown-'

def send(addr, data):
	for c in clients:
		if c['address'] == addr:
			c['conn'].send(data)
			return True
	return False

def send_to_all(data, category = ['admins', 'slaves']):
	for c in clients:
		if 'admins' in category and c['type'] == CLIENT_ADMIN:
			c['conn'].send(data)
		if 'slaves' in category and c['type'] == CLIENT_SERVER:
			if c['state'] == 0:
				c['conn'].send(data)
	return True
