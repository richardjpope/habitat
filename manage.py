from flask import Flask
from flask.ext.script import Manager, Option, Command
import shapefile
import models

app = Flask(__name__)

class ImportOSM(Command):

    def run(self):

        #delete existing
        models.Fence.drop_collection()

        print "Starting to read shape files"
        #https://pypi.python.org/pypi/pyshp#reading-shapefiles
        shape_reader = shapefile.Reader("/Users/richardpope/Downloads/greater-london-latest/buildings")
        records = shape_reader.records()
        shapes = shape_reader.shapes()

        for i in xrange(0, len(shapes)):
            fence = models.Fence()
            fence.category = 'building'
            fence.polygon = shapes[i].__geo_interface__
            fence.save()

manager = Manager(app)
manager.add_command('import-osm', ImportOSM())

if __name__ == "__main__":
    manager.run()
