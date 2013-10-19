from darkcloud.common.hmac import HMAC
from darkcloud.common.signals import signals

import json

class RequestFramework():
    def __init__(self, use_hmac = True):
        self.use_hmac = use_hmac

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

    def _remote_cmd(self, data, **kwargs):
        return False

    def _get_client(self, addr):
        return addr

    def _exec_function(self, conn, args):
        print args
        function = 'action_%s' % (args['action'])
        return getattr(self, function)(
            client=self._get_client(conn.remote_addr()),
            **args
        )

        return False

    def parse(self, conn, message):
        if not message:
            return False

        try:
            msg = json.loads(message)
        except ValueError:
            return conn.sendresp(self.reply(500, "This doesn't looks like JSON data..."))

        if 'action' not in msg and 'info' not in msg:
            return False

        if 'action' in msg:
            ret = self._exec_function(conn, msg)
            if ret == False:
                conn.sendresp(self.reply(500))
            else:
                conn.sendresp(ret)
        elif 'info' in msg:
            # handle info in it's special way
            signals.emit('data:on_info', conn.remote_addr(), msg['info'])
