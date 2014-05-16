from behave import *
from habitat import app

@when('I am within {distance:d} meters of "{location}"')
def step_impl2(context, distance, location):
    """ Check if you are near a longitude/latitude """

    import re
    from datetime import datetime, timedelta
    from habitat import models

    #match = re.search('^\[-?(\d+\.?\d*),-?(\d+\.?\d*)\]$', location)
    match = re.search('^\[(-?\d+\.?\d*),(-?\d+\.?\d*)\]$', location)
    assert match

    radians = float(distance) / 6378100 # radius of the earth

    since = datetime.utcnow() - timedelta(minutes=5)

    lnglat = [float(match.group(1)), float(match.group(2))]

    location = models.Location.objects(lnglat__geo_within_sphere=[lnglat, radians], occured_at__lte=since)

    assert len(location) > 0
