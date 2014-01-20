import urllib
from flask import Flask
from flask.ext.script import Manager, Option, Command
import shapefile
import os
import zipfile
from habitat import models
from habitat import tasks
from habitat import app
from habitat import db

data_dir = data_dir = '%s/import-data' % os.path.dirname(os.path.abspath(__file__))

class DownloadOSM(Command):

    def run(self):

        #create download directory if does not exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print "Created download directory at %s" % data_dir

        #download zip files
        osm_zipped_urls = ['http://download.geofabrik.de/europe/great-britain/england/greater-london-latest.shp.zip',]
        for url in osm_zipped_urls:

            file_name = url.split('/')[len(url.split('/')) -1]
            urllib.urlretrieve(url, "%s/%s" % (data_dir, file_name))

            #upzip
            osm_zipped_file = zipfile.ZipFile("%s/%s" % (data_dir, file_name), 'r')
            osm_zipped_file.extractall(data_dir)
            osm_zipped_file.close()

class ImportOSM(Command):

    def run(self):

        #delete existing
        models.Fence.drop_collection()

        print "Starting to read shape files"
        #https://pypi.python.org/pypi/pyshp#reading-shapefiles
        shape_reader = shapefile.Reader("%s/%s" % (data_dir, "buildings"))
        records = shape_reader.records()
        shapes = shape_reader.shapes()

        for i in xrange(0, len(shapes)):
            fence = models.Fence()
            fence.category = 'building'
            fence.polygon = shapes[i].__geo_interface__
            fence.save()

class Setup(Command):

    def run(self):
        print "Creating database ..."
        db.create_all()


class RunScenarios(Command):

    def run(self):
        tasks.run_scenarios()


manager = Manager(app)
manager.add_command('import-osm', ImportOSM())
manager.add_command('download-osm', DownloadOSM())
manager.add_command('run-scenarios', RunScenarios())
manager.add_command('setup', Setup())

if __name__ == "__main__":
    manager.run()
