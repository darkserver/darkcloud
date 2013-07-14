import select
import socket
import sys
import Queue

from darkcloud.common.connectionsocket import ConnectionSocket
from darkcloud.common.logger import Logger
from darkcloud.common.signals import signals

log = Logger('server')

class ConnectionSocketServer(ConnectionSocket):
    def __init__(self, host, port):
        ConnectionSocket.__init__(self)

        self.host = host
        self.port = port

        self.connections = {}
        self.connection_inputs = [self.socket]
        self.connection_outputs = []
        self.message_queues = {}

        try:
            self.socket.bind((self.host, self.port))
            self.socket.setblocking(False)
            log.info("Listening on %s:%s" % (self.host, self.port))
        except socket.error as err:
            log.critical(err[1])
            sys.exit(1)

        self.socket.listen(5)

    def __del__(self):
        self.socket.close()

    def pool(self):
        readable, writable, exception = select.select(
            self.connection_inputs,
            self.connection_outputs,
            self.connection_inputs,
        )

        for s in readable:
            if s is self.socket:
                """Incoming connection"""

                new_connection, new_address = s.accept()
                address = "%s:%s" % new_address
                log.info("Client %s connected" % (address))
                s.setblocking(False)

                self.connection_inputs.append(new_connection)
                self.connections[address] = ConnectionSocket(use_socket=new_connection)
                self.message_queues[new_connection] = Queue.Queue()

                signals.emit('connection:connected', self.connections[address])
            else:
                """Current connection"""

                try:
                    address = "%s:%s" % s.getpeername()
                except socket.error:
                    try:
                        self.connection_outputs.remove(s)
                    except ValueError:
                        pass

                data = self.connections[address].recv()
                if data:
                    self.message_queues[s].put(data)

                    if s not in self.connection_outputs:
                        self.connection_outputs.append(s)

                    signals.emit('connection:data_received', self.connections[address], data)
                else:
                    log.info("Client %s disconnected" % address)

                    if s in self.connection_outputs:
                        self.connection_outputs.remove(s)
                        writable.remove(s)

                    self.connection_inputs.remove(self.connections[address].socket)
                    self.connections[address].socket.close()

                    del self.message_queues[s]
                    del self.connections[address]

                    signals.emit('connection:disconnected', address)

        for s in writable:
            try:
                next_msg = self.message_queues[s].get_nowait()
            except Queue.Empty:
                address = "%s:%s" % s.getpeername()
                self.connection_outputs.remove(s)
            else:
                try:
                    address = "%s:%s" % s.getpeername()
                except socket.error:
                    self.connection_outputs.remove(s)

        for s in exception:
            address = "%s:%s" % connection.socket.getpeername()

            log.critical("Handling exceptional condition for %s!" % address)
            self.connection_inputs.remove(s)
            if s in self.connection_outputs:
                self.connection_outputs.remove(s)
            self.connections[address].socket.close()

            del self.connections[address]

        return True
