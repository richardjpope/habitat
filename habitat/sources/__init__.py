from flask import abort
from abc import ABCMeta, abstractmethod
from habitat import app
from datetime import timedelta

class SourceBase():
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def schedule(self):
        """A list containing a dictionary of functions to schedule"""

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def __init__(self, app, celery, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        #schedule tasks
        for item in self.schedule:
            schedule_item = {'%s-%s' % (item['function'], self.name): {
            'task': 'habitat.sources.%s.%s' % (self.name, item['function']),
            'schedule': timedelta(seconds=item['seconds'])
            }}

            app.config['CELERYBEAT_SCHEDULE'].update(schedule_item)

    @abstractmethod
    def settings_view():
        """A settings page for handling any settings (or returning a 404)"""

    @abstractmethod
    def fetch_events():
        """Get any data from this source"""

    @abstractmethod
    def process_event(event):
        """Process a newly fetched event"""
