##Requirements:
- Python
- MongoDB
- Rabit MQ


##Setup

1) Create a virtual environent:

$ virtualenv .

2) Enter virtual environment

$ source bin/activate

3) Install requirements:

$ pip install -r requirements.txt

## Running

1) Enter virtual environment:

$ source bin/activate

2) Start Mongo DB (if it isnt already running):

$ mongod

3) Start app:

$ python app.py

## Importing OSM data

* Download shape files from http://download.geofabrik.de



##Running the app

$ source bin/activate
$ mongod
$ celery -A app.celery worker -B -l info
$ python app.py