import os
import glob
from behave import parser as behave_parser
from behave import model as behave_models
from datetime import datetime
from habitat import tasks, app
from mongoengine import StringField, PolygonField, DateTimeField, PointField, StringField, DictField, DynamicDocument, Document, ObjectIdField, BooleanField, URLField, ListField, ReferenceField
from mongoengine import signals
from mongoengine import DoesNotExist
import hashlib

class AuthClient(Document):
    client_id = StringField(max_length=40, required=True, unique=True)
    name = StringField(max_length=55, required=True)
    client_secret = StringField(max_length=200, required=True)
    is_confidential = BooleanField()

    _redirect_uris = StringField()
    _default_scopes = StringField()

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            print self._redirect_uris.split()
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    def validate_scopes(self, scopes):
        return True

class AuthGrant(Document):

    client = ReferenceField(AuthClient)
    code = StringField(max_length=200, required=True)
    redirect_uri = URLField(required=True)
    expires = DateTimeField()
    _scopes = StringField()
    #
    # def validate_redirect_uri(redirect_uri):
    #     return True

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

class AuthToken(Document):
    client = ReferenceField(AuthClient)
    token_type = StringField()
    access_token = StringField(unique=True)
    refresh_token = StringField(unique=True)
    expires = DateTimeField()
    _scopes = StringField()

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Location(DynamicDocument):

    latlng = PointField()
    occured_at = DateTimeField()

    def to_dict(self):
        return {'id': str(self.id), 'latlng': self.latlng, 'occured_at': self.occured_at.isoformat()}

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        tasks.run_scenarios.delay()

signals.post_save.connect(Location.post_save, sender=Location)

def __init__(self, _id=None):
        self.id = _id

#not a mongo model, so not sure it should really be here.
class Scenario():

    @property
    def modified_at(self):

        if self.id:
            file_path = Scenario._get_feature_file_name(self.id)
            return datetime.fromtimestamp(os.path.getmtime(file_path))
        else:
            return None

    def __init__(self, _id=None, code=None):
        self.id = _id
        self.code = code

    def validate(self):
        try:
            behave_parser.parse_feature(self.code)
            return True
        except behave_parser.ParserError:
            return False

    def save(self):

        if not self.id:
            self.id = hashlib.sha1(self.code).hexdigest()

        file_path = Scenario._get_feature_file_name(self.id)
        file_ref = open(file_path, 'w')
        file_ref.write(self.code)
        return self

    def delete(self):
        file_path = Scenario._get_feature_file_name(self.id)
        os.remove(file_path)

    def to_dict(self):
        return {'id': str(self.id), 'code': self.code, 'occured_at': self.modified_at.isoformat()}

    @staticmethod
    def get(_id):

        file_path = Scenario._get_feature_file_name(_id)
        print file_path

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
        return os.path.join(app.config['SCENARIOS_DIR'], feature_id + '.feature')

    @staticmethod
    def list():

        result = []

        if not os.path.isdir(app.config['SCENARIOS_DIR']):
            raise IOError("Scenarios directory does not exist")

        for file_path in glob.glob(app.config['SCENARIOS_DIR'] + '/*.feature'):

            _id = os.path.basename(file_path).split('.')[0]
            scenario = Scenario.get(_id)
            result.append(scenario)

        return result
