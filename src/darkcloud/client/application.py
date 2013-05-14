import readline
import sys
from socket import gethostbyaddr

from darkcloud.common.connectionsocketclient import ConnectionSocketClient
from darkcloud.common.signals import signals

import darkcloud.settings as settings

def on_connect(client):
    client.send("auth adm admin 1234\n");
    print  ">> %s <<" % client.pool()

def on_recv(client, data):
    print " >>> %s <<< "% data

def main():
    settings.DEBUG = False

    client = ConnectionSocketClient()
    if client == False:
        sys.exit(1)

    signals.connect('connection:connected', on_connect)
    signals.connect('connection:data_received', on_recv)

    client.connect()

    x = client.remote_addr().split(':')
    remote = '%s:%s' % (gethostbyaddr(x[0])[0], x[1])

    try:
        cmd = ''
        while True:
            cmd = raw_input('\033[0;33m-(\033[1;33m%s\033[0;33m)->\033[0m ' % remote)
            if cmd == 'quit':
                raise EOFError
            if not cmd:
                continue

            client.send(cmd)
            client.pool()
    #        print client.pool()

    #except KeyboardInterrupt:
    #    pass
    except EOFError:
        pass

    print("\nQuitting...")

    client.disconnect()

    del client
