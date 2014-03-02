from habitat import celery
from habitat import app
from runner import Configuration
from runner import Runner

@celery.task
def run_scenarios():

    configuration = Configuration(command_args='') # important: without this, the sys.args from celery worker confuse it
    configuration.scenarios_dir = app.config['SCENARIOS_DIR']
    configuration.plugins_dir = app.config['PLUGINS_DIR']
    configuration.format = ['pretty']
    configuration.verbose = True

    runner = Runner(configuration)
    failed = runner.run()
