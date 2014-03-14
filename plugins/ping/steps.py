from behave import *
from habitat import app

@then('ping "{url}"')
def step_impl(context, url):
	""" Ping a URL """
	import urllib2
	assert context.failed is False
	try:
		urllib2.urlopen(url)
	except urllib2.HTTPError:
		app.logger.error("An error occured pinging url %s" % url)
