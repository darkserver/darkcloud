from darkcloud.common.hmac import HMAC

def reply(retcode, data = None):
	# We can use HTTP status codes. Can't we?
	messages = {
		200 : 'OK',
		400 : 'Bad Request',
		401 : 'Unauthorized',
		403 : 'Forbidden',
		404 : 'Not Found',
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

def check_cmd(data, level):
	for d in data:
		if d in level:
			if type(level[d]) is dict:
				return check_cmd(data[1:], level[d])
			else:
				return (level[d], data[1:])
	return False
