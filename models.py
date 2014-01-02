from mongoengine import StringField, PolygonField, DateTimeField, PointField, StringField, DictField, DynamicDocument, Document
import datetime

class Fence(DynamicDocument):
    category = StringField(max_length=25, required=True)
    polygon = PolygonField()

class Event(DynamicDocument):
    occcured_at = DateTimeField()

class Location(DynamicDocument):
    location = PointField()
    occcured_at = DateTimeField()

class Setting(Document):
    key = StringField(max_length=25, required=True, unique=True)
    value = DictField(required=True)