import json
import geojson
import glob
import os
import imp
import re
import inspect
import dateutil.parser
from flask import make_response
from flask.ext.restful import reqparse, abort, Api, Resource
from mongoengine import DoesNotExist, ValidationError
from habitat import api, models, app, oauth
from flask_restful.utils import cors

#validators for various field types (must return ValueError if fails)
def geojson_point(data):

    try:
        point =  geojson.Point(type=data['type'], coordinates=data['coordinates'])
        return data
    except ValueError:
        raise ValueError

def feature_code(data):

    scenario = models.Scenario(code=data)

    if scenario.validate():
        return data
    else:
        raise ValueError

def iso_date(data):
    return dateutil.parser.parse(data)

def mongo_get_or_abort(_id, cls):
    try:
        return cls.objects.get(id=_id)
    except ValidationError:
        abort(404, message="%s %s does not exist" % (cls._class_name, _id))
    except DoesNotExist:
        abort(404, message="%s %s does not exist" % (cls._class_name, _id))

class Location(Resource):

    def options(self):
        pass

    @oauth.require_oauth('locations:view')
    def get(oauth, self, _id):
        return mongo_get_or_abort(_id, models.Location).to_dict()

class Locations(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(Locations, self).__init__()

    def options(self):
        pass

    @oauth.require_oauth('locations:view')
    def get(oauth, self):
    	result = []
        locations = models.Location.objects()
        for location in locations:
        	result.append(location.to_dict())
        return result

    @oauth.require_oauth('locations:add')
    def post(oauth, self):

        self.parser.add_argument('lnglat', type=geojson_point, required=True, location='json', help="lnglat must be a valid geojson point")
        self.parser.add_argument('occured_at', type=iso_date, required=True, location='json', help="occured_at must be a valid date time")
        args = self.parser.parse_args()

        try:
            location = models.Location()
            location.lnglat = args['lnglat']
            location.occured_at = args['occured_at']
            location.save()
        except ValidationError, e:
            app.logger.error('Failed to save a location: %s' % e)

        return location.to_dict(), 201

class Scenarios(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(Scenarios, self).__init__()


    # def options(self):
    #   return {'Allow' : 'PUT' }, 200, { 'Access-Control-Allow-Origin': '*','Access-Control-Allow-Methods' : 'PUT,GET' }

    def options(self):
        pass

    @oauth.require_oauth('scenarios')
    def get(oauth, self):
        result = []
        scenarios = models.Scenario.list()
        for scenario in scenarios:
            result.append(scenario.to_dict())
        return result, 200

    @oauth.require_oauth('scenarios')
    def post(oauth, self):

        self.parser.add_argument('code', type=feature_code, required=True, location='json', help="must be a valid scenario")

        args = self.parser.parse_args()

        try:
            scenario = models.Scenario()
            scenario.code = args['code']
            scenario.save()
            return scenario.to_dict(), 201
        except IOError:
            return 'Unable to create scenario', 500

class Scenario(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(Scenario, self).__init__()

    def _get_or_abort(self, _id):
        try:
            return models.Scenario.get(_id)
        except IOError:
            abort(404, message="Scenario %s does not exist" % (_id))

    @oauth.require_oauth('scenarios')
    def options(oauth, self):
      pass

    @oauth.require_oauth('scenarios')
    def get(oauth, self, _id):

        return self._get_or_abort(_id).to_dict()

    @oauth.require_oauth('scenarios')
    def put(oauth, self, _id):

        scenario = self._get_or_abort(_id)

        self.parser.add_argument('code', type=feature_code, required=True, location='json', help="must be a valid scenario")
        args = self.parser.parse_args()

        scenario.code = args['code']
        try:
            scenario.save()
            return scenario.to_dict(), 200
        except IOError:
            return 'Unable to save scenario', 500

    @oauth.require_oauth('scenarios')
    def delete(oauth, self, _id):
        try:
            scenario = models.Scenario.get(_id)
            scenario.delete()
            return '', 204
        except IOError:
            abort(404, message="Scenario %s does not exist" % (_id))

class Plugins(Resource):

    @oauth.require_oauth('scenarios')
    def options(oauth, self):
        pass

    @oauth.require_oauth('scenarios')
    def get(oauth, self):

        results = []
        plugins = []

        #get plugin directories
        for file_path in glob.glob(app.config['PLUGINS_DIR'] + '/*/__init__.py'):
            path = os.path.dirname(file_path)
            name = os.path.basename(path)
            plugins.append({'name': name, 'path':path})

        #extract steps
        for plugin in plugins:
            steps = []
            step_source = imp.load_source(plugin['name'], plugin['path'] + '/steps.py')
            functions = inspect.getmembers(step_source, predicate=inspect.isroutine)

            for function in functions:

                if function[1].__module__ == step_source.__name__:
                    code = inspect.getsourcelines(function[1])[0][0]

                    #tidy up
                    regex = re.compile('@given|@when|@then')
                    match = regex.match(code)

                    if match:
                        about = inspect.getdoc(function[1])
                        code = code.replace('@given(\'', 'Given ').replace('@when(\'', 'When ').replace('@then(\'', 'Then ').replace('\n', '').replace('\')', '')

                        #store step
                        steps.append({'code': code, 'about':about})

            results.append({'name': plugin['name'], 'steps': steps})

        return results

#routes
api.add_resource(Locations, '/locations')
api.add_resource(Location, '/locations/<string:_id>')
api.add_resource(Scenarios, '/scenarios')
api.add_resource(Scenario, '/scenarios/<string:_id>')
api.add_resource(Plugins, '/plugins')
