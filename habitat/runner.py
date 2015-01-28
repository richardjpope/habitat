import os
import glob
import models
from behave import matchers, parser
from behave.step_registry import setup_step_decorators
from behave.formatter import formatters
from behave.runner import ModelRunner, PathManager, path_getrootdir, Context, exec_file
from behave.runner_util import parse_features, FileLocationParser, FileNotFoundError
from behave.configuration import ConfigError, Configuration

class Configuration(Configuration):

    def __init__(self, command_args=None, load_config=True, verbose=None, **kwargs):
        self.scenarios_dir = None
        self.plugins_dir = None
        super(Configuration, self).__init__(command_args, load_config, verbose)

class Runner(ModelRunner):

    def __init__(self, config):
        super(Runner, self).__init__(config)
        self.base_dir = None

    def load_steps(self):

        step_globals = {'use_step_matcher': matchers.use_step_matcher,}
        setup_step_decorators(step_globals)
        default_matcher = matchers.current_matcher

        for file_path in glob.glob(self.config.plugins_dir + '/*/steps.py'):
            step_module_globals = step_globals.copy()
            exec_file(file_path, step_module_globals)
            matchers.current_matcher = default_matcher

    def feature_locations(self):

        locations = []
        for path in glob.glob(self.config.scenarios_dir + '/*.feature'):
            location = FileLocationParser.parse(path)
            locations.append(location)

        return locations


    def run(self):

        self.context = Context(self)
        self.load_steps()

        #Parse all features
        scenarios = models.Scenario.list()

        features = []
        for scenario in scenarios:
            feature = parser.parse_feature(scenario.code, language=self.config.lang)
            features.append(feature)

        self.features.extend(features)

        #Run all features
        stream_openers = self.config.outputs
        self.formatters = formatters.get_formatter(self.config, stream_openers)
        return self.run_model()
