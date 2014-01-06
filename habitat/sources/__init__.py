from flask import abort
from abc import ABCMeta, abstractmethod

class SourceBase():
    __metaclass__ = ABCMeta

    fetch_delay_seconds = 60

    @property
    def name(self):
        return self.__class__.__name__.lower()

    def __init__(self, app, celery, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        #add routes
        self.register_urls(app)

        #add tasks
        self.register_tasks(celery)

        self.schedule_tasks(app)

        #schedule fetch data
        # schedule_item = {'fetch-data-%s' % self.name: {
        #     'task': 'sources.%s.fetch_data' % self.name,
        #     'schedule': timedelta(seconds=self.fetch_delay_seconds)
        # }}

        # app.config['CELERYBEAT_SCHEDULE'].update(schedule_item)

    @abstractmethod
    def settings_view(self):
        """A settings page for handling any settings (or returning a 404)"""

    @abstractmethod
    def register_urls(self, app):
        """Register any URLs the source requires (e.g. settings)"""
        #app.add_url_rule("/settings/%s" % self.name, "%s_settings" % self.name, view_func=self.settings_view)

    @abstractmethod
    def register_tasks(self, celery):
        """Register any tasks the source requires"""
        #celery.task(self.fetch_data)

    @abstractmethod
    def schedule_tasks(self, app):
        """Schedule any recurring tasks"""
        #celery.task(self.fetch_data)

    @abstractmethod
    def fetch_events(self):
        """Get any data from this source"""

