from shifts import *
import sys

def generate_shifts(pacific_start):

	dst = is_dst(pacific_start, pacific)

	if dst:
		hour = 10
	else:
		hour = 9

	start = pacific_start

	short_dt = datetime.timedelta(hours = 4)
	long_dt = datetime.timedelta(hours = 12)

	shifts = [shift(start, start+short_dt,"Pacific")]

	for i in range(1,21):
		s = shifts[-1].stop
		if i % 3 != 0:
			nxt = shift(s,s+short_dt,"Pacific")
		else:
			nxt = shift(s+long_dt,s+long_dt+short_dt,"Pacific")

		shifts.append(nxt)

	# Monday is 0
	return reorder(shifts, 0)
	"""
	startday = start.weekday()
	# need to make sure a Monday is in the
	# first position in the list
	return cycle(shifts,3*(7-startday))
	"""

def init_schedule(utc_start):

	cal, a_names, av, h_names, emails, times = do_google_init()

	observers = []
	shifts = generate_shifts(utc_start.astimezone(pacific))

	for aa,a_name in enumerate(a_names):
		o = None
		for hh,h_name in enumerate(h_names):

			if clean(h_name) != clean(a_name):
				continue

			if o == None:
				o = observer(a_name, emails[hh])
				for i,s in enumerate(shifts):
					o.availability[s] = av[aa][i]

			t = times[hh]
			for s in shifts:
				if s.match(t):
					o.karma += shift.karma
					if abs((t-utc_start).total_seconds()) < 7*24*3600:
						if is_weekend(utc_start.astimezone(pacific)):
							for ss in shifts[-6:]:
								o.availability[ss] = False

		if o == None:
			print>>sys.stderr, "%s not found in handoff" % (a_name)
			continue
		observers.append(o)

	sch = schedule()
	sch.observers = observers
	sch.shifts = shifts


	return sch