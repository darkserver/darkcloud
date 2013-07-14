import socket
import Queue
from time import sleep

from darkcloud.common.connectionsocket import ConnectionSocket
from darkcloud.common.hmac import HMAC
from darkcloud.common.logger import Logger
from darkcloud.common.signals import signals

import darkcloud.settings as settings

import json

class ConnectionSocketClient(ConnectionSocket):
    def __init__(self, host, port):
        ConnectionSocket.__init__(self)

        self.host = host
        self.port = port

        self.connected = None
        self.data = None

    def __del__(self):
        self.disconnect()

    def connect(self):
        log = Logger('client')
        try:
            if self.connected == False:
                sleep(1)
            ConnectionSocket.__init__(self)
            self.socket.connect((self.host, self.port))
            self.connected = True

            log.info("Connected to %s:%s" % (self.host, self.port))
            signals.emit('connection:connected', self)
        except socket.error as err:
            if self.connected == False:
                log.critical("Can't connect to %s:%s: %s" % (self.host,
                                                             self.port,
                                                             err[1]))
            elif self.connected or self.connected == None:
                log.critical("Can't connect to %s:%s: %s" % (self.host,
                                                             self.port,
                                                             err[1]))
                self.connected = False

        return self.connected

    def disconnect(self):
        self.connected = False
        self.close()

        signals.emit('connection:disconnected', False)

    def send(self, data):
        hmac = HMAC()
        signed_message = hmac.sign_message("", "", data)

        try:
            ConnectionSocket.send(self, signed_message)
        except socket.error as err:
            self.lost(err)

    def lost(self, err = None):
        if err:
            print("\033[1;31mConnection to %s:%s lost\033[0m: %s" % (settings.HUB_HOST, settings.HUB_PORT, err))
        else:
            print("\033[1;31mConnection to %s:%s lost\033[0m" % (settings.HUB_HOST, settings.HUB_PORT))

        signals.emit('connection:lost')
        self.disconnect()
        return self.connect()

    def pool(self):
        try:
            if self.socket and self.connected:
                self.data = self.recv()
                if not self.data:
                    self.lost()
                    return None

                self.data = self.data.rstrip('\n')

                signals.emit('connection:data_received', self, self.data)
            else:
                if self.connected or self.connected == None:
                    print("Not connected. Connecting. Autoreconnect every 5 second")
                self.connect()
        except socket.error as err:
            return self.lost(err)

        return self.data

    def is_connected(self):
        return self.connected
