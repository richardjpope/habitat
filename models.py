from app import db
import datetime

class Fence(db.DynamicDocument):
    category = db.StringField(max_length=25, required=True)
    polygon = db.PolygonField()

class Event(db.DynamicDocument):
    occcured_at = db.DateTimeField()

class Location(db.DynamicDocument):
    location = db.PointField()
    occcured_at = db.DateTimeField()

class Setting(db.Document):
    key = db.StringField(max_length=25, required=True, unique=True)
    value = db.DictField(required=True)