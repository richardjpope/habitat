from app import db
import datetime

class Fence(db.DynamicDocument):
    category = db.StringField(max_length=25, required=True)
    polygon = db.PolygonField()
