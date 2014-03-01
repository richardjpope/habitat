import os
import glob
from behave import parser as behave_parser
from behave import model as behave_models
from datetime import datetime
from habitat import tasks, app
from mongoengine import StringField, PolygonField, DateTimeField, PointField, StringField, DictField, DynamicDocument, Document, ObjectIdField
from mongoengine import signals
from mongoengine import DoesNotExist

class Location(DynamicDocument):
    latlng = PointField()
    occured_at = DateTimeField()

    def to_dict(self):
        return {'id': str(self.id), 'latlng': self.latlng, 'occured_at': self.occured_at.isoformat()}

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        tasks.run_scenarios.delay()

signals.post_save.connect(Location.post_save, sender=Location)

#not a mongo model, so not sure it should really be here.
class Scenario():

    @property
    def modified_at(self):
        file_path = Scenario._get_feature_file_name(self.id)
        return datetime.fromtimestamp(os.path.getmtime(file_path))

    def __init__(self, _id=None, code=None):
        self.id = _id
        self.code = code

    def validate(self):
        pass

    def save(self):
        pass

    def delete(self):
        file_path = Scenario._get_feature_file_name(self.id)
        os.remove(file_path)

    def create(self):
        pass

    def to_dict(self):
        return {'id': str(self.id), 'code': self.code, 'occured_at': self.modified_at.isoformat()}

    @staticmethod
    def get(_id):

        file_path = Scenario._get_feature_file_name(_id)
        feature = behave_parser.parse_file(file_path)
        code = Scenario._feature_to_string(feature)
        _id = os.path.basename(file_path).split('.')[0]

        return Scenario(_id, code)

    @staticmethod
    def _feature_to_string(feature):
        result = "%s: %s \n" % (feature.keyword, feature.name)
        for scenario in feature:
            result = "%s    %s: %s \n" % (result, scenario.keyword, scenario.name)
            for step in scenario.steps:
                result = "%s        %s %s \n" % (result, step.keyword, step.name)
        return result

    @staticmethod
    def _get_feature_file_name(feature_id):
        feature_id = feature_id.replace('.', '').replace('/', '') #make safe(er) to stop ../../
        return os.path.join(app.config['FEATURE_DIR'], feature_id + '.feature')

    @staticmethod
    def list():
        result = []
        for file_path in glob.glob(app.config['FEATURE_DIR'] + '/*.feature'):

            _id = os.path.basename(file_path).split('.')[0]
            scenario = Scenario.get(_id)
            result.append(scenario)

        return result
