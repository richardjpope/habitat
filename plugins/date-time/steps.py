from behave import *
from habitat import app

@when('The time is "{time}"')
def step_impl(context, time):
    """ Check if it is a given time (use 24 hour clock)"""
    import time as python_time
    from datetime import datetime
    now = datetime.now()
    check_time = python_time.strptime(time, '%H:%M')
    assert check_time == now

    # import re
    # from datetime import datetime, timedelta
    # from habitat import models
    #
    # match = re.search('^\[-?(\d+\.?\d*),-?(\d+\.?\d*)\]$', location)
    # assert match
    #
    # #latlng = [float(match.group(1)), float(match.group(2))]
    # #location = models.Location.objects(latlng__near=latlng, latlng__max_distance=distance, occured_at__lte=since)
    # since = datetime.now() - timedelta(minutes=5)
    # lat = float(match.group(1))
    # lng = float(match.group(2))
    # # location = models.Location.objects(latlng__within_distance=[(lat,lng),distance], occured_at__gte=since)
    # location = [1]
    # assert len(location) > 0
