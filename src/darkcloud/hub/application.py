from time import sleep

import darkcloud.hub.client as client
from darkcloud.hub.request import Request
from darkcloud.hub.connectionsocketserver import ConnectionSocketServer
from darkcloud.common.signals import signals

def main():
    server = ConnectionSocketServer()
    request = Request()

    signals.connect('connection:connected', client.add)
    signals.connect('connection:disconnected', client.remove)
    signals.connect('connection:data_received', request.parse)

    signals.connect('data:on_info', client.on_info)

    try:
        while server.pool():
            sleep(0.01)
    except KeyboardInterrupt:
        pass

    del server
