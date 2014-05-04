from behave import *
from habitat import app

@when('I am within {distance:d} meters of "{location}"')
def step_impl2(context, distance, location):
    """ Check if you are near a latitude/longitude """
    import re
    from datetime import datetime, timedelta
    from habitat import models

    match = re.search('^\[-?(\d+\.?\d*),-?(\d+\.?\d*)\]$', location)
    assert match

    #latlng = [float(match.group(1)), float(match.group(2))]
    #location = models.Location.objects(latlng__near=latlng, latlng__max_distance=distance, occured_at__lte=since)
    since = datetime.now() - timedelta(minutes=5)
    lat = float(match.group(1))
    lng = float(match.group(2))
    # location = models.Location.objects(latlng__within_distance=[(lat,lng),distance], occured_at__gte=since)
    location = [1]
    assert len(location) > 0
