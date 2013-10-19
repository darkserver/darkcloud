import darkcloud.settings as settings
from darkcloud.common.hmac import HMAC
from darkcloud.common.logger import Logger

import socket
import json

log = Logger('connection')

class ConnectionSocket():
    def __init__(self, use_socket=None):
        if use_socket:
            self.socket = use_socket
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def recv(self):
        try:
            data = self.socket.recv(settings.BUFFER_SIZE).rstrip('\n')
            if not data:
                return None
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

    def _add_hash_response(self, data):
        # TODO: generate hash in top of message
        return data

    def sendjson(self, data):
        try:
            ConnectionSocket.send(self, self._add_hash_response(json.dumps(data, sort_keys=False, indent=2)))
        except socket.error as err:
            self.lost(err)

    # obsolete
    def sendcmd(self, data):
        self.sendjson({'cmd': data})

    def sendresp(self, data):
        self.sendjson({'resp': data})

    def sendinfo(self, data):
        self.sendjson({'info': data})

    def remote_addr(self):
        try:
            return "%s:%s" % (self.socket.getpeername())
        except socket.error as e:
            log.critical("Connection unexpectedly closed: %s" % (self._addr, e))
            return "0.0.0.0:0"

    def appendQueue(self, data):
        self.queue.put(data)

    def close(self):
        self.socket.close()
