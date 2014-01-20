# from mongoengine import StringField, PolygonField, DateTimeField, GeoPointField, StringField, DictField, DynamicDocument, Document, ObjectIdField
# from mongoengine import signals
# from mongoengine import DoesNotExist
from habitat import db
import datetime
from habitat import tasks
#from geoalchemy import GeometryColumn, Point
from flask.ext.sqlalchemy import models_committed, Session

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    guid = db.Column(db.String(255), nullable=False, unique=True)
    source = db.Column(db.String(25), nullable=False)
    occured_at = db.DateTime()
    data = db.Column(db.Text(), nullable=False)

    @staticmethod
    def guid_exists(guid):
        # try:
        event = Event.query.get(guid=guid)
        #     return True
        # except DoesNotExist:
        #     return False

class Location(db.Model):
    __tablename__ = 'location'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    # latlng = GeoPointField()
    # latlng = GeometryColumn(Point(2))
    event_id = db.Column(db.Integer, nullable=False) #intentionally set no foreign key here.
    occured_at = db.DateTime()

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        tasks.run_scenarios.delay()

class Setting(db.Model):

    __tablename__ = 'setting'
    key = db.Column(db.String(25), nullable=False, primary_key=True, unique=True)
    value = db.Column(db.Text(), nullable=False)

# class Fence(DynamicDocument):
#     category = StringField(max_length=25, required=True)
#     polygon = PolygonField()
  
#models_committed.connect(Location.post_save, sender=Location)
