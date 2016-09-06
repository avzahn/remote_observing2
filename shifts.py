from google_client import *
import datetime
import pytz
import re
import copy
import sys

from gmail import *

pacific = pytz.timezone("America/Los_Angeles")
utc = pytz.utc

def datetime_compare(dt0,dt1):
	attrs=['year','day','hour','minute']
	for attr in attrs:
		if getattr(dt0,attr) != getattr(dt1,attr):
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
	out =  re.sub('[^a-z]', '', s)
	return out

def is_weekend(start):
	"""
	start must be a localized datetime

	TODO: This would be a good place to detect holidays
	"""
	if start.weekday() > 4:
		return True
	if start.weekday() == 4:
		# Friday nights count as weekends
		if start.hour >= 12:
			return True

class observer(object):
	def __init__(self, name, email):
		self.name = name
		self.email = email
		self.karma = 0
		self.shift = None
		self.availability = {}
		
	def dump_availability(self):
		l = sorted(self.availability.items(),key=lambda x: x[0])
		out = ''
		for item in l:
			out += '%s :: %s\n' % (item[0].time_str(),bool_to_html(item[1]))
		return out
		
	def get_reminder(self, subject):
		
		msg = reminder.substitute(
			availability=indent(self.dump_availability()),
			sheet_url=sheet_url)
		
		msg = MIMEText(msg,'html')
		msg['Subject'] = subject
		
		return msg
		
	def send_reminder(self,subject):
		msg = self.get_reminder(subject)
		send(msg,self.email)
			


class shift(object):
	def __init__(self, start, stop, region):
		self.start = start # must be a localized datetime
		self.stop = stop
		self.region = region # name string (ie, "Pacific")
		self.weekend = is_weekend(start)
		self.observer = observer(name='UNFILLED', email='avzahn06@gmail.com')
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
		
	def __lt__(self, s):
		return self.start < s.start

	def __eq__(self,s):
		a = datetime_compare(self.start,s.start)
		b = datetime_compare(self.stop, s.stop)
		return a and b

	def __hash__(self):
		return self.start.day


	def time_str(self):
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

		return "%s - %s" % (a,b)

	def __str__(self):

		return"%s :: %s" % (self.time_str(),self.observer.name)

	def __repr__(self):
		return self.__str__()
		

class schedule(object):
	def __init__(self):

		self.observers = []
		self.shifts = []
		self.cal = None

	def publish(self):
		for s in self.shifts:
			self.cal.post_shift(s)

	def __str__(self):
		out = ""
		for s in self.shifts:
			out += str(s)
			out += "\n"

		return out
		
	def remind_all(self):
		
		now = datetime.datetime.now()
		month = now.month
		day = now.day
		
		subject = "Polarbear remote observing newsletter %s/%s"%(month,day)
		
		for obs in self.observers:
			obs.send_reminder(subject)

	def schedule(self):

		observers = sorted(self.observers,key=lambda o: o.karma)
		shifts = reorder(self.shifts, 5)


		for s in shifts:
			for o in observers:
				if o.availability[s]:
					o.shift = s
					s.observer = o
					observers.remove(o)
					break

		all_emails = ''
		for o in self.observers:
			all_emails += o.email











		
