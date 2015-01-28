import os
# from pytz import all_timezones
from flask.ext.script import Manager, Command, prompt_bool, prompt, prompt_pass, prompt_choices
from habitat import app
from celery.task.control import discard_all as celery_discard_all

class Setup(Command):

    def run(self):
        local_config_exists = os.path.isfile('local_config.py')
        if local_config_exists:
            if not prompt_bool("Overwrite existing settings?"):
                return

        admin_username = prompt('Choose an admin user name')
        admin_pass = prompt_pass('Choose an admin password')
        email_address = prompt('What email address do you want to send alerts to?')
        time_zone = prompt('What time zone are we in?', default='Europe/London')
        database_name = prompt_pass('Choose a database name', default='habitat')

class ResetQueues(Command):

    def run(self):
        celery_discard_all()

manager = Manager(app)
manager.add_command('reset-queues', ResetQueues())
manager.add_command('setup', Setup())

if __name__ == "__main__":
    manager.run()
