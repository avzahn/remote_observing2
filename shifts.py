from google_client import *
import datetime
import pytz
import re
import copy

pacific = pytz.timezone("America/Los_Angeles")
utc = pytz.utc

def datetime_compare(dt0,dt1):
	attrs=['year','day','hour','minute']
	for attr in attrs:
		if getattr(dt0,attr) != getattr(dt1,attr)
			return False
	return True

def cycle(l,n):
	"""
	move the first n elements of l to the end
	"""
	end = l[:n]
	start = l[n:]
	return start + end

def reorder(shifts,day):
	# monday is 0
	n = len(shifts)
	for i,s in enumerate(shifts):
		if s.start.weekday() == day:
			return cycle(shifts, i)

def is_dst(utc_datetime,tz):
	return utc_datetime.astimezone(tz).dst() != datetime.timedelta(0)

def clean(name):
	"""
	remove all nonalphanumeric characters from a string
	and convert to lower case
	"""
	s = name.lower()
	return re.sub('[^a-z]', '', s)

def is_weekend(start):
	"""
	start must be a localized datetime

	TODO: This would be a good place to detect holidays
	"""
	if start.weekday() > 4:
		return True
	if start.weekday() == 4:
		# Friday nights count as weekends
		if start.hour > 14:
			return True

class observer(object):
	def __init__(self, name, email):
		self.name = name
		self.email = email
		self.karma = 0
		self.shift = None
		self.availability = {}

class shift(object):
	def __init__(self, start, stop, region):
		self.start = start # must be a localized datetime
		self.stop = stop
		self.region = region # name string (ie, "Pacific")
		self.weekend = is_weekend(start)
		self.observer = observer(name='UNFILLED', email='polarbear2@googlegroups.com')
		self.karma = 10

		if self.weekend == True:
			self.karma = 25

	def match(self,utc_handoff_time):

		utc_stop = self.stop.astimezone(utc)

		diff = 0

		diff += 24*60*abs(utc_handoff_time.weekday() - utc_stop.weekday())
		diff += 60 * abs(utc_handoff_time.hour - utc_stop.hour)
		diff += abs(utc_handoff_time.minute - utc_stop.minute)

		return diff < 120

	def __eq__(self,s):
		a = datetime_compare(self.start,s.start)
		b = datetime_compare(self.end, s.end)
		return a and b

	def __hash__(self):
		return self.start.day

	def __str__(self):
		s,e = self.start, self.stop
		
		h0, h1 = s.hour, e.hour
		m0, m1 = s.minute, e.minute
		d0, d1 = s.weekday(), e.weekday()
		
		if d0 == d1:
			a = s.strftime( "%a %d %I:%M %p")
			b = e.strftime( "%I:%M %p %Z")
		else:
			a = s.strftime( "%a %d %I:%M %p")
			b = e.strftime( "%a %d %I:%M %p %Z")

		return"%s - %s :: %s" % (a,b,self.observer.name)

class schedule(object):
	def __init__(self):

		self.observers = []
		self.shifts = []
		self.cal = None

	def publish(self):
		for s in shifts:
			self.cal.post_shift(shift)

	def __str__(self):
		out = ""
		for s in self.shifts:
			out += str(s)
			out += "\n"

		return out

	def schedule(self):

		observers = copy.copy(self.observers.sort(lambda o: o.karma))
		shifts = reorder(self.shifts, 5)








		
