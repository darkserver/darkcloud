from time import sleep

import sys

import darkcloud.hub.client as client
from darkcloud.hub.core import full_name, version
from darkcloud.hub.request import Request
from darkcloud.hub.connectionsocketserver import ConnectionSocketServer
from darkcloud.common.config import Config
from darkcloud.common.logger import Logger
from darkcloud.common.signals import signals

def main():
    log = Logger('hub')

    log.info('Starting %s %s' % (full_name, version))

    cfg = Config('hub')
    if not cfg.is_loaded():
        sys.exit(1)

    server = ConnectionSocketServer(cfg['listen'].host(),
                                    cfg['listen'].port())
    request = Request()

    signals.connect('connection:connected', client.add)
    signals.connect('connection:disconnected', client.remove)
    signals.connect('connection:data_received', request.parse)

    signals.connect('data:on_info', client.on_info)

    try:
        while server.pool():
            sleep(0.01)
    except KeyboardInterrupt:
        sys.stdout.write('\r')
        log.info('Exiting on user request (Ctrl+C)')
        pass

    del server
