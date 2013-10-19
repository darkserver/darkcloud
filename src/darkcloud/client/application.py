import json
import readline
import sys
from socket import gethostbyaddr

from darkcloud.common.connectionsocketclient import ConnectionSocketClient
from darkcloud.common.config import Config
from darkcloud.common.signals import signals

import darkcloud.client.views

import darkcloud.settings as settings

last_cmd = ''

cfg = None

def on_connect(client):
    client.sendjson({
        'action': 'auth',
        'type': 'adm',
        'name': 'admin',
        'password': '1234',
    })
    print("%s" % client.pool())

def on_recv(client, data):
    if not last_cmd:
        return
    try:
        c = getattr(darkcloud.client.views,
                    last_cmd.split(' ')[0])(json.loads(data)['resp']['data'])
    except AttributeError:
        print("%s" % data)

def main():
    global cfg

    cfg = Config('client')

    if not cfg.is_loaded():
        sys.exit(1)

    client = ConnectionSocketClient(cfg['hub'].host(),
                                    cfg['hub'].port())
    if client == False:
        sys.exit(1)

    signals.connect('connection:connected', on_connect)
    signals.connect('connection:data_received', on_recv)

    client.connect()

    x = client.remote_addr().split(':')
    remote = '%s:%s' % (gethostbyaddr(x[0])[0], x[1])

    global last_cmd

    try:
        cmd = ''
        while True:
            cmd = raw_input("%s " % (cfg['prompt'].ansi() % remote))
            if cmd == 'quit':
                raise EOFError
            if not cmd:
                continue
            last_cmd = cmd

            client.sendjson({
                'action': cmd
            })
            client.pool()

    except KeyboardInterrupt:
        print("quit")
        pass
    except EOFError:
        pass

    print("Quitting...")

    client.disconnect()

    del client
