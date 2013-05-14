import json
import sys
from time import sleep
from socket import gethostbyaddr

from darkcloud.hub.request import Request
from darkcloud.common.connectionsocketclient import ConnectionSocketClient
from darkcloud.common.signals import signals

import darkcloud.settings as settings

def on_connect(client):
    client.sendcmd("auth slave %s imslave!" % (gethostbyaddr('127.0.0.1')[0]))
    x = json.loads(client.pool())['resp']['data']
    print("Connected to %s %s" % (x['fullname'], x['version']))
    # FIXME TODO read real capabilities
    client.sendinfo({
        'caps': {'www': ['nginx', 'apache'], 'db': ['mysql']},
    })

def main():
    client = ConnectionSocketClient()
    request = Request()

    if client == False:
        sys.exit(1)

    signals.connect('connection:connected', on_connect)
    signals.connect('connection:data_received', request.parse)

    client.connect()

    try:
        while client.pool():
            pass
    except KeyboardInterrupt:
        pass

    client.disconnect()

    del client
