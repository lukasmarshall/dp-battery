import threading

class ThreadWorker():
	def __init__(self, func):
		self.thread = None
		self.data = None
		self.func = self.save_data(func)

	def save_data(self, func):
		# modify the function to save its return data.
		def new_func(*args, **kwargs):
			self.data = func(*args, **kwargs)

		return new_func

	def start(self, params):
		self.data = None
		returnValue = None

		if self.thread is not None: #the thread has started.
			if self.thread.isAlive():
				returnValue =  'running'
		else: #the thread has not yet started. start it.
			self.thread = threading.Thread(target = self.func, args=params)
			self.thread.start()
			returnValue =  'started'

		return returnValue
	def status(self):
		if self.thread is None:
			return 'not_started'
		else: 
			if self.thread.isAlive():
				return 'running'
			else:
				return 'finished'

	def get_results(self):
		if self.thread is None:
			return 'not_started'
		else:
			if self.thread.isAlive():
				return 'running'
			else:
				return self.data
