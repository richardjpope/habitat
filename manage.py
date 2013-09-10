from flask import Flask
from flask.ext.script import Manager, Option, Command
import shapefile
import models
import os

app = Flask(__name__)

class DownloadOSM(Command):

    def run(self):

        print "hello"
        data_dir = '%s/import-data' % os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

class ImportOSM(Command):

    def run(self):

        #delete existing
        models.Fence.drop_collection()

        print "Starting to read shape files"
        #https://pypi.python.org/pypi/pyshp#reading-shapefiles
        dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(dir, "import-data/greater-london-latest/buildings")
        print path
        shape_reader = shapefile.Reader(path)
        records = shape_reader.records()
        shapes = shape_reader.shapes()

        for i in xrange(0, len(shapes)):
            fence = models.Fence()
            fence.category = 'building'
            fence.polygon = shapes[i].__geo_interface__
            fence.save()

manager = Manager(app)
manager.add_command('import-osm', ImportOSM())
manager.add_command('download-osm', DownloadOSM())

if __name__ == "__main__":
    manager.run()
