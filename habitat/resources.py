import os
import glob
import json
import geojson
import dateutil.parser
from datetime import datetime
from flask import make_response
from flask.ext.restful import reqparse, abort, Api, Resource
from mongoengine import DoesNotExist, ValidationError
from behave import parser as behave_parser
from behave import model as behave_models
from habitat import api, models, app

def get_feature_file_name(feature_id):
    feature_id = feature_id.replace('.', '').replace('/', '') #make safe(er) to stop ../../     
    return os.path.join(app.config['FEATURE_DIR'], feature_id + '.feature')

def feature_to_string(feature):
    result = "%s: %s \n" % (feature.keyword, feature.name)
    for scenario in feature:
        result = "%s    %s: %s \n" % (result, scenario.keyword, scenario.name)
        for step in scenario.steps:
            result = "%s        %s %s \n" % (result, step.keyword, step.name)
    return result
    
def geojson_point(data):
    try:
        point =  geojson.Point(type=data['type'],coordinates=data['coordinates'])
        return data
    except ValueError:
        raise ValueError

def iso_date(data):
    return dateutil.parser.parse(data)

def get_or_abort(_id, cls):
    try:
        return cls.objects.get(id=_id)
    except ValidationError:
        abort(404, message="%s %s does not exist" % (cls._class_name, _id))
    except DoesNotExist:
        abort(404, message="%s %s does not exist" % (cls._class_name, _id))

class Location(Resource):
        
    def get(self, _id):
        return get_or_abort(_id, models.Location).to_dict()

    def delete(self, _id):
        location = get_or_abort(_id, models.Location)
        location.delete()
        return '', 204

class Locations(Resource):
    
    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(TaskAPI, self).__init__()
           

    def get(self):
    	result = []
        locations = models.Location.objects()
        for location in locations:
        	result.append(location.to_dict())
        return result

    def post(self):

        self.parser.add_argument('latlng', type=geojson_point, required=True, location='json', help="must be a valid geojson point")
        self.parser.add_argument('occured_at', type=iso_date, required=True, location='json', help="must be a valid date time")
        args = self.parser.parse_args()

        try:
            location = models.Location()
            location.latlng = args['latlng']
            location.occured_at = args['occured_at']
            location.save()
        except ValidationError, e:
            app.logger.error('Failed to save a location: %s' % e)

        return str(location.id)

class Scenarios(Resource):
    def get(self):
        features = []
        for feature_file_path in glob.glob(app.config['SCENARIOS_DIR'] + '/*.feature'):

            feature = behave_parser.parse_file(feature_file_path)
            feature_id = os.path.basename(feature_file_path).split('.')[0]
            modified_at = datetime.fromtimestamp(os.path.getmtime(feature_file_path)).isoformat()

            features.append({'code': feature_to_string(feature), 'modified_at': modified_at, 'feature_id': feature_id})
        
        return features
        

#routes
api.add_resource(Locations, '/locations')
api.add_resource(Location, '/locations/<string:_id>')
api.add_resource(Scenarios, '/scenarios')