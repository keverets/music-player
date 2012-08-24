from collections import deque
from threading import Condition
class OnRequestQueue:
	class QueueEnd:
		def __init__(self):
			self.q = deque()
			self.cond = Condition()
			self.cancel = False
	def __init__(self):
		self.queues = set()
	def put(self, item):
		for q in self.queues:
			with q.cond:
				if q.cancel: continue
				q.q.append(item)
				q.cond.notify()
	def cancelAll(self):
		for q in self.queues:
			with q.cond:
				q.cancel = True
				q.cond.notify()
		self.queues.clear()
	def read(self):
		q = self.QueueEnd()
		self.queues.add(q)
		while True:
			with q.cond:
				l = list(q.q)
				q.q.clear()
				cancel = q.cancel
				if not l and not cancel:
					q.cond.wait()
			for item in l:
				yield item
			if cancel: break

class EventCallback:
	def __init__(self, targetQueue, name=None):
		self.targetQueue = targetQueue
		self.name = name
	def __call__(self, *args, **kwargs):
		self.targetQueue.put((self, args, kwargs))
	def __repr__(self):
		return "<EventCallback %s>" % self.name

class initBy(property):
	def __init__(self, initFunc):
		property.__init__(self, fget = self.fget)
		self.initFunc = initFunc
	def fget(self, inst):
		if hasattr(self, "value"): return self.value
		self.value = self.initFunc(inst)
		return self.value

class oneOf(property):
	def __init__(self, *consts):
		property.__init__(self, fget = self.fget, fset = self.fset)
		assert len(consts) > 0
		self.consts = consts
		self.value = consts[0]
	def fget(self, inst):
		return self
	def fset(self, inst, value):
		assert value in self.consts
		self.value = value


def setTtyNoncanonical(fd, timeout=0):
	import termios
	old = termios.tcgetattr(fd)
	new = termios.tcgetattr(fd)
	new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
	# http://www.unixguide.net/unix/programming/3.6.2.shtml
	#new[6] [termios.VMIN] = 1
	#new[6] [termios.VTIME] = 0
	new[6] [termios.VMIN] = 0 if timeout > 0 else 1
	timeout *= 10 # 10ths of second
	if timeout > 0 and timeout < 1: timeout = 1
	new[6] [termios.VTIME] = timeout
		
	termios.tcsetattr(fd, termios.TCSANOW, new)
	termios.tcsendbreak(fd,0)