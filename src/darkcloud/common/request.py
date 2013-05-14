from darkcloud.common.hmac import HMAC

import json

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

    def _exec_function(self, conn, data):
        try:
            (function, args) = self.check_cmd(data, self.cmds)
            function = '_parse_%s' % (function)
            return getattr(self, function)(
                data = args,
                remote_addr = conn.remote_addr()
            )
        except IndexError:
            return False
        except TypeError:
            return False

    def parse(self, conn, message):
        if not message:
            return False

        try:
            msg = json.loads(message)
        except ValueError:
            return conn.sendresp(self.reply(500, "This doesn't looks like JSON data..."))

        if 'cmd' not in msg and 'info' not in msg:
            return False

        if self.use_hmac:
            try:
                msg_hash = msg['hmac']
            except KeyError:
                return conn.sendresp(self.reply(403))
            hmac = HMAC()

            if not hmac.compare(msg_hash, msg):
                return conn.sendresp(self.reply(403))

        if 'cmd' in msg:
            ret = self._exec_function(conn, msg['cmd'].split(' '))
            if ret == False:
                conn.sendresp(self.reply(500))
            else:
                conn.sendresp(ret)
        elif 'info' in msg:
            # handle info in it's special way
            ret = self.set_info(msg['info'])
            if ret == False:
                conn.sendresp(self.reply(404))

    def set_info(self, data):
        """Do nothing here
        There's should be method in ihnerited class"""
        pass
