import select
import socket
import sys
import Queue

from darkcloud.common.connectionsocket import ConnectionSocket
from darkcloud.common.signals import signals
import darkcloud.settings as settings

class ConnectionSocketServer(ConnectionSocket):
	def __init__(self):
		ConnectionSocket.__init__(self)

		self.connections = {}
		self.connection_inputs = [self.socket]
		self.connection_outputs = []
		self.message_queues = {}

		try:
			self.socket.bind((settings.HUB_HOST, settings.HUB_PORT))
			self.socket.setblocking(False)
		except socket.error as err:
			print("\033[1;33m%s\033[0m" % err)
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
				print("[%s] BEGIN" % (address))
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
					print("[%s] END" % address)

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

			print("Handling exceptional condition for %s!" % address)
			self.connection_inputs.remove(s)
			if s in self.connection_outputs:
				self.connection_outputs.remove(s)
			self.connections[address].socket.close()

			del self.connections[address]

		return True
