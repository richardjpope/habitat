from behave import *
from habitat import app

# @then(u'email me a message "{subject}" - "{message}"')
@then(u'email me "{subject}" - "{message}"')
def step_impl(context, subject, message):
	from email.mime.text import MIMEText
	from subprocess import Popen, PIPE

	assert context.failed is False

	msg = MIMEText(message)
  	msg["From"] = app.config['EMAIL_FROM']
  	msg["To"] = app.config['EMAIL_TO']
  	msg["Subject"] = subject
  	p = Popen([app.config['SENDMAIL_PATH'], "-t"], stdin=PIPE)
  	p.communicate(msg.as_string())


@then('ping "{url}"')
def step_impl(context, url):
	import urllib2
	assert context.failed is False
	try:
		urllib2.urlopen(url)
	except urllib2.HTTPError:
		app.logger.error("An error occured pinging url %s" % url)


