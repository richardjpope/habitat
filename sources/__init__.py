from flask import abort
from datetime import timedelta

class SourceBase():

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

		#schedule fetch data
		schedule_item = {'fetch-data-%s' % self.name: {
        	'task': 'sources.%s.fetch_data' % self.name,
        	'schedule': timedelta(seconds=self.fetch_delay_seconds)
    	}}

		app.config['CELERYBEAT_SCHEDULE'].update(schedule_item)

	def settings_view(self):
		abort(404)

	def register_urls(self, app):
		app.add_url_rule("/settings/%s" % self.name, "%s_settings" % self.name, view_func=self.settings_view)

	def register_tasks(self, celery):
		celery.task(self.fetch_data)


	def fetch_data(self):
		return NotImplemented

