class Signals():
	def __init__(self):
		self.handlers = {}

	def connect(self, signal_name, function_handler):
		if signal_name not in self.handlers:
			self.handlers[signal_name] = []
		self.handlers[signal_name].append(function_handler)
		return True

	def disconnect(self, signal_name):
		try:
			self.handlers.remove(signal_name)
			return True
		except KeyError:
			print("Signal handler %s doesn't exists!" % (signal_name))
			return False

	def emit(self, signal_name, *args):
		try:
			for signal in self.handlers[signal_name]:
				signal(*args)
			return True
		except KeyError:
			print("Signal handler %s doesn't exists!" % (signal_name))
			return False

signals = Signals()
