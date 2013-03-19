from darkcloud.common.hmac import HMAC

class RequestFramework():
	def __init__(self, use_hmac = True):
		self.use_hmac = use_hmac
		self.cmds = {}

	def reply(self, retcode, data = None):
		# We can use HTTP status codes. Can't we?
		messages = {
			200 : 'OK',
			400 : 'Bad Request',
			401 : 'Unauthorized',
			403 : 'Forbidden',
			404 : 'Not Found',
			500 : 'Internal Server Error',
		}

		try:
			message = messages[retcode]
		except KeyError:
			message = 'Unknown Return Code'

		return {
			'status' : {
				'code' : retcode,
				'message' : message,
			},
			'data' : data,
		}

	def check_cmd(self, data, level):
		for d in data:
			if d in level:
				if type(level[d]) is dict:
					return self.check_cmd(data[1:], level[d])
				else:
					return (level[d], data[1:])
		return False

	def parse(self, conn, msg):
		if not msg:
			return False

		if self.use_hmac:
			try:
				(msg_hash, msg) = msg.split(' ', 1)
			except ValueError:
				return conn.sendjson(self.reply(403))
			hmac = HMAC()

			if not hmac.compare(msg_hash, msg):
				return conn.sendjson(self.reply(403))

		data = msg.strip().split(' ')

		if data[0] == 'json':
			return False

		try:
			(function, args) = self.check_cmd(data, self.cmds)
			function = '_parse_%s' % (function)
			out = getattr(self, function)(
				data = args,
				remote_addr = conn.remote_addr()
			)
			conn.sendjson(out)
		except IndexError:
			conn.sendjson(self.reply(404))
		except TypeError:
			conn.sendjson(self.reply(404))
