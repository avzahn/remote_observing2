import smtplib
from email.mime.text import MIMEText
from string import Template

def send(mime,dst,
	srv='smtp.gmail.com:587',
	src_addr='pbremoteshift@gmail.com',
	usr='pbremoteshift',
	pswd='pb4000#$'):

	server = smtplib.SMTP(srv)
	server.starttls()
	server.login(usr,pswd)
	server.sendmail(src_addr, dst, mime.as_string())
	server.quit()


def indent(s):	
	out = ''
	for line in s.split('\n'):
		out += "<font face='Courier New'>  &emsp; \t%s </font> <br> \n"%line
	return out

def bool_to_html(b):
	
	color = 'red'
	text = 'Not Available'
	
	if b:
		color = 'green'
		text = 'Available'
		
	return "<font color='%s'>%s</font>"%(color,text)
	
	
		

reminder =\
"""\
Hi there! <br><br>

If you're getting this message, it probably means you filled out a row for yourself in the <a href="$sheet_url">polarbear remote observing availability spreadsheet</a>.<br><br>

Every Sunday night after 10 PM, the remote observing scheduler uses this sheet to decide shifts for the coming Wednesday to Wednesday observing cycle, among other important life and death matters.<br><br>

For the cycle just scheduled, you were marked available for <br><br>

<br>

$availability

<br>

You can change your availablity on the sheet any time before it runs and be guaranteed not to a get shift for which you have marked "No" for the coming week.<br><br>

If you were assigned a shift for the next cycle, you should get a Google Calendar notification email.<br><br>

Finally, remember to file a handoff report after your shift by messaging polarbearalerts with "! handoff " on Slack. This is the only way that the scheduler can credit you for for an observing shift, which allows it to avoid scheduling you for consecutive weekends.<br><br>

<font color="green">***This message sponsored by Elleflot International Next Day Courier LLC***</font>
"""

reminder = Template(reminder)

sheet_url = 'https://docs.google.com/spreadsheets/d/1STjLDnzNczsTKd3ZOgaOL9MDHMzzW_y44MQCMza7Zm4/edit#gid=0'
