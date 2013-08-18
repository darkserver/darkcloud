import json
import sys
from time import sleep
from socket import gethostbyaddr

from darkcloud.hub.request import Request
from darkcloud.common.connectionsocketclient import ConnectionSocketClient
from darkcloud.common.config import Config
from darkcloud.common.logger import Logger
from darkcloud.common.signals import signals

cfg = None

def on_connect(client):
    client.sendcmd("auth slave %s imslave!" % (gethostbyaddr('127.0.0.1')[0]))
    welcome_data = client.pool()
    x = json.loads(welcome_data)['resp']['data']
    client.sendinfo({
        'caps': cfg['plugins'],
    })

def main():
    global cfg

    log = Logger('manager')
    log.info("Starting DarkCloud Manager")

    cfg = Config('manager')
    if not cfg.is_laoded():
        sys.exit(1)

    client = ConnectionSocketClient(cfg['hub'].host(),
                                    cfg['hub'].port())
    request = Request()

    if client == False:
        sys.exit(1)

    signals.connect('connection:connected', on_connect)
    signals.connect('connection:data_received', request.parse)

    client.connect()

    while True:
        client.pool()

    client.disconnect()

    del client
