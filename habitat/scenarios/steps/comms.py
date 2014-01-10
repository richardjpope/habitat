import urllib2
from behave import *
from habitat import app

# @then('send me a message "{message}"')
# def step_impl(context, message):
# 	print context.failed
# 	assert context.failed is False
# 	print message

@then('ping "{url}"')
def step_impl(context, url):
	assert context.failed is False
	try:
		urllib2.urlopen(url)
	except urllib2.HTTPError:
		app.logger.error("An error occured pinging url %s" % url)