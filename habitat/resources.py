import json
import geojson
import dateutil.parser
from flask import make_response
from flask.ext.restful import reqparse, abort, Api, Resource
from mongoengine import DoesNotExist, ValidationError
from habitat import api, models, app

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

    def __init__(self):
        self.parser = reqparse.RequestParser()
        super(Scenarios, self).__init__()

    def get(self):
        result = []
        scenarios = models.Scenario.list()
        for scenario in scenarios:
            result.append(scenario.to_dict())

        return result

class Scenario(Resource):

    def get(self, _id):
        try:
            return models.Scenario.get(_id).to_dict()
        except IOError:
            abort(404, message="Scenario %s does not exist" % (_id))
        # return get_or_abort(_id, models.Location).to_dict()

    def delete(self, _id):
        try:
            scenario = models.Scenario.get(_id)
            scenario.delete()
            return '', 204
        except IOError:
            abort(404, message="Scenario %s does not exist" % (_id))

    # def post(self):
    #
    #     self.parser.add_argument('code', type=str, required=True, location='json', help="must contain a valid given/when/then scenario")
    #     args = self.parser.parse_args()
    #
    #     feature = behave_parser.parse_feature(args['code'])
    #     file_name = generate_feature_file_name(feature)
    #     file_path = get_feature_file_name(file_name)
    #
    #     file_ref = open(feature_file_path, 'w')
    #     file_ref.write(utils.feature_to_string(feature))
    #
    #     return os.path.basename(file_path).split('.')[0]
    #

#routes
api.add_resource(Locations, '/locations')
api.add_resource(Location, '/locations/<string:_id>')
api.add_resource(Scenarios, '/scenarios')
api.add_resource(Scenario, '/scenarios/<string:_id>')
