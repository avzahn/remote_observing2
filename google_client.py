"""
This file is an attempt at consolidating all google API related code in
one place, mostly because figuring out two different google APIs was painful
and keeping a centralized example on how to use them seems important.

In summary, we want to read availability and handoff information from a pair
of google spreadsheets, do work on it elsewhere, and then update a google
calendar with the schedule we arrive at.

To do this inside a standalone application like this one, google requires us
to launch a browser at an authentication request page where the user can
grant access to their spreadsheets and calendars by copying and pasting an
access code that the webpage issues back into the application.

See google documentation for more information about the magic strings in this
file.

The only things of external relevance here are the calendar class, which 
provides a convenience method for posting shifts to the google calendar,
and do_google_init, which returns all the useful spreadsheet information and
a calendar object that provides access to the remote observing calendar.

"""
from oauth2client.client import OAuth2WebServerFlow
import webbrowser
import httplib2
from apiclient.discovery import build
import datetime
import gspread
import pytz

utc = pytz.utc

# Specifies what permissions we're asking google for. One of these may be
# redundant, but it doesn't really matter. Note that all of these have to be
# set to enabled on the user's google developer console for the polarbear
# service account.
scope = 'https://www.googleapis.com/auth/drive \
https://www.googleapis.com/auth/calendar \
https://spreadsheets.google.com/feeds'

# More values from the developer console. These I think uniquely specify that
# we're trying to associate this application with the polarbear service account
client_id = '629542510716-2rdm5bbfrjg9k97mm00stt5gliv217h8.apps.googleusercontent.com'
client_secret = '_bxlaJdmImQUgu7I1WI_Osoq'

# Controls some unimportant things about the authentication page the user sees.
# The most interesting thing we can change with this is to have the access code
# that the user currently has to copy and paste manually into the application
# appear in the browser window title bar, where in principle we could
# programmatically grab it.
redirect_uri='urn:ietf:wg:oauth:2.0:oob'

# Identifying information for the polarbear documents we want
calendar_id = '14i5g7mue5c6637mo0fdo01l60@group.calendar.google.com'
availability_name = "Remote_Observing_Availability"
handoff_name = "handoff_test_copy"

def get_credentials(scope=scope,
	client_id=client_id,
	client_secret=client_secret,
	redirect_uri=redirect_uri):
	"""
	Return an oauth2 credentials object that should authorize us to do
	everything we need to do. The credentials returned here are used by
	get_clients() to instantiate the clients we interact with to get and
	change google data.
	"""

	flow = OAuth2WebServerFlow(scope=scope,
		client_id=client_id,
		client_secret=client_secret,
		redirect_uri=redirect_uri)

	auth_uri = flow.step1_get_authorize_url()
	webbrowser.open(auth_uri)
	code = raw_input('auth code')
	credentials = flow.step2_exchange(code)

	return credentials

class calendar(object):
	def __init__(self, service, calendar_id):
		self.id = calendar_id
		self.service = service

	def post_shift(self, shift):
		"""
		put a shift on a google calendar.
		"""
		text ='%s - %s' % (shift.region, shift.observer.name)

		event = {
			'start': {
				'dateTime': shift.start.isoformat(),
				'timeZone': shift.start.tzinfo.zone,
		  	},
			'end': {
				'dateTime': shift.stop.isoformat(),
				'timeZone': shift.stop.tzinfo.zone,
			},
			'attendees': [
				{'email': shift.observer.email},
			],
			'reminders': {
				'useDefault': False,
				'overrides': [
					{'method': 'email', 'minutes': 24 * 60},
					{'method': 'email', 'minutes': 10},
				],
			},
			'description': text,
			'summary':text,
			'gadget.title': text
		}
		self.service.events().insert(calendarId=self.id,
			sendNotifications=True,
			body=event).execute()

def get_clients(credentials,
	calendar_id=calendar_id,
	availability_name=availability_name,
	handoff_name=handoff_name):

	http = credentials.authorize(httplib2.Http())
	cal = build('calendar', 'v3', http=http)
	cal = calendar(cal,calendar_id)

	gs = gspread.authorize(credentials)
	availability = gs.open(availability_name).sheet1
	handoff = gs.open(handoff_name).sheet1

	return cal, availability, handoff

def handoff_time_str_to_dt(s):
	"""
	Convert the time string from the handoff reports to a utc localized datetime
	"""
	# the datetime module's strptime doesn't handle non zero padded values...
	ss = s.split(' ')
	time = map(int,ss[1].split(':'))
	date = map(int,ss[0].split('/'))
	args = [date[2], date[0], date[1], time[0], time[1], time[2]]
	return utc.localize(datetime.datetime(*args))

def get_last_handoffs(handoff, n=210):
	"""
	return the last n [name,email,handoff time] in the handoff records
	"""
	_all = handoff.get_all_values()
	h = [ [r[1], handoff_time_str_to_dt(r[5]), r[8] ] for r in _all[-n:] ]
	names = [hh[0] for hh in h]
	times = [hh[1] for hh in h]
	emails = [hh[2] for hh in h]
	return names,emails,times


def do_google_init():
	credentials = get_credentials()
	cal, availability, handoff = get_clients(credentials)
	h_names, emails, times = get_last_handoffs(handoff)
	
	a = availability.get_all_values()[2:] # first two rows have no information
	a_names = [aa[1] for aa in a]

	av = []
	for row in a:
		# ignore the existence of "maybe" option for now
		av.append([ r.lower() == 'yes' for r in row[2:] ])

	return cal, a_names, av, h_names, emails, times
