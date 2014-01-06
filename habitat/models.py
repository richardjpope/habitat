from mongoengine import StringField, PolygonField, DateTimeField, PointField, StringField, DictField, DynamicDocument, Document
import datetime

class Event(DynamicDocument):
    guid = StringField(max_length=255, required=True, unique=True)
    source = StringField(max_length=25, required=True) 
    occcured_at = DateTimeField()
    data = DictField(required=True)

class Location(DynamicDocument):
    location = PointField()
    occcured_at = DateTimeField()

class Setting(Document):
    key = StringField(max_length=25, required=True, unique=True)
    value = DictField(required=True)

class Fence(DynamicDocument):
    category = StringField(max_length=25, required=True)
    polygon = PolygonField()