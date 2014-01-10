from behave import *
from habitat import models
from datetime import datetime, timedelta
import json
import re
from habitat import app

#@given('I am within {distance:d} meters of lat/lng "{latlng}"')
@when(u'I am within {distance:d} meters of "{location}"')
def step_impl(context, distance, location):

	match = re.search('^\[(\d+\.?\d*),(\d+\.?\d*)\]$', location)
	assert match

	latlng = [float(match.group(1)), float(match.group(2))]
	since = datetime.now() - timedelta(minutes=5)
	location = models.Location.objects(latlng__near=latlng, latlng__max_distance=distance, occured_at__lte=since)
	assert len(location) > 0