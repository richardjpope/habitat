import datetime
from habitat import tasks
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
