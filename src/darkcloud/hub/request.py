import darkcloud.hub.client as client
import darkcloud.hub.core as core
from darkcloud.common.hmac import HMAC
from darkcloud.common.request import reply, check_cmd

# decorators...

def needs_auth(fn):
	def wrapped(**kwargs):
		isauth, cl = client.authorized(kwargs['remote_addr'])
		if isauth == client.CLIENT_ADMIN:
			return fn(kwargs['data'])
		else:
			return reply(401)
	return wrapped

# code

cmds = {
	'auth' : 'auth',
	'list' : 'list',
}

def parse(conn, msg, use_hmac = True):
	if use_hmac:
		(msg_hash, msg) = msg.split(' ', 1)
		hmac = HMAC()

		if not hmac.compare(msg_hash, msg):
			return conn.sendjson(reply(403))

	data = msg.strip().split(' ')

	try:
		(function, args) = check_cmd(data, cmds)
		conn.sendjson(globals()['_parse_%s' % function](
			data = args,
			remote_addr = conn.remote_addr()
		))
	except IndexError:
		pass
	except TypeError:
		conn.sendjson(reply(404))

def _parse_auth(data, **kwargs):
	print "CCC"
	if client.auth(kwargs['remote_addr'], data[0], data[1], data[2]):
		return reply(200, {'fullname' : core.full_name, 'name' : core.name, 'version' : core.version})
	else:
		return reply(403)

@needs_auth
def _parse_list(data, **kwargs):
	if len(data) > 1:
		return reply(200, client.list_all([data[1]]))
	else:
		return reply(200, client.list_all())
