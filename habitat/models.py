from mongoengine import StringField, PolygonField, DateTimeField, PointField, StringField, DictField, DynamicDocument, Document, ObjectIdField
from mongoengine import signals
import datetime
from habitat import tasks

class Event(DynamicDocument):
    guid = StringField(max_length=255, required=True, unique=True)
    source = StringField(max_length=25, required=True) 
    occcured_at = DateTimeField()
    data = DictField(required=True)

class Location(DynamicDocument):
    latlng = PointField()
    event_id = ObjectIdField
    occcured_at = DateTimeField()

    @classmethod
    def post_save(cls, sender, document, **kwargs):
        tasks.run_scenarios.delay()

class Setting(Document):
    key = StringField(max_length=25, required=True, unique=True)
    value = DictField(required=True)

class Fence(DynamicDocument):
    category = StringField(max_length=25, required=True)
    polygon = PolygonField()

    
signals.post_save.connect(Location.post_save, sender=Location)
