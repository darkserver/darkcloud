import darkcloud.settings as settings
from darkcloud.common.hmac import HMAC

import socket
import json

class ConnectionSocket():
    def __init__(self, use_socket = None):
        if use_socket:
            self.socket = use_socket
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def recv(self):
        try:
            data = self.socket.recv(settings.BUFFER_SIZE).rstrip('\n')
        except socket.error as err:
            print("\033[1;31mSOCKET ERROR:\033[0m %s" % err)
            return None

        if settings.DEBUG:
            print("\033[0;36mrecv\033[0m> \033[0;33m%s\033[0m" % (data))

        return data

    def send(self, data):
        if settings.DEBUG:
            print("\033[0;33msend\033[0m> \033[0;33m%s\033[0m" % (data))

        self.socket.send(data)

    def _create_response(self, data):
        hmac = HMAC()
        return {
            'hmac': hmac.sign_message("", "", data), # FIXME TODO add real salt
        }

    def sendjson(self, data):
        try:
            ConnectionSocket.send(self, json.dumps(data, sort_keys = False, indent = 2))
        except socket.error as err:
            self.lost(err)

    def sendresp(self, data):
        x = self._create_response(data)
        x['resp'] = data
        self.sendjson(x)

    def sendcmd(self, data):
        x = self._create_response(data)
        x['cmd'] = data
        self.sendjson(x)

    def remote_addr(self):
        return "%s:%s" % (self.socket.getpeername())

    def appendQueue(self, data):
        self.queue.put(data)

    def close(self):
        self.socket.close()
