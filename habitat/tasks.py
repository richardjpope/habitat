from habitat import celery

@celery.task
def run_scenarios():

    from behave.configuration import Configuration, ConfigError
    from behave.runner import Runner
    from behave.runner_util import InvalidFileLocationError, InvalidFilenameError, FileNotFoundError
    from behave.parser import ParserError

    failed = True
    configuration = Configuration(command_args='') # important: without this, the sys.args from celery worker confuse it
    configuration.paths = [app.config['FEATURE_DIR']]
    configuration.format = ['pretty']
    configuration.verbose = True

    app.logger.info('Running scenarios')
    runner = Runner(configuration)

    try:
        failed = runner.run()
    except ParserError, e:
        return "ParseError: %s" % e
    except ConfigError, e:
        return "ConfigError: %s" % e
    except FileNotFoundError, e:
        return "FileNotFoundError: %s" % e
    except InvalidFileLocationError, e:
        return "InvalidFileLocationError: %s" % e
    except InvalidFilenameError, e:
        return "InvalidFilenameError: %s" % e

    return 'worked'