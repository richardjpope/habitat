from flask import Flask, request, redirect, render_template, json, Response
from flask.ext.mongoengine import MongoEngine
from mongoengine import connect
import jinja2
import os
import models
import re

# settings
MONGO_URL = os.environ.get("MONGOHQ_URL")
app = Flask(__name__)

if MONGO_URL:
    credentials = re.sub(r"(.*?)//(.*?)(@hatch)", r"\2",MONGO_URL)
    username = credentials.split(":")[0]
    password = credentials.split(":")[1]
    app.config["MONGODB_DB"] = MONGO_URL.split("/")[-1]
    connect(
        MONGO_URL.split("/")[-1],
        host=MONGO_URL,
        port=1043,
        username=username,
        password=password
    )
app.config.update(
    DEBUG = True,
    MONGODB_SETTINGS = {'DB': "openactivity"}
)

db = MongoEngine(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/edit")
def edit():
    return render_template('edit.html')

@app.route("/me")
def results():
    return render_template('results.html')

@app.route("/api/")
def api():
    #building: http://localhost:5000/api/?lng=-0.1206612&lat=51.517323
    #road: http://localhost:5000/api/?lng=-0.120442&lat=51.517546
    #buildings = models.Fence.objects(polygon__geo_intersects=[float(-0.1206612), float(51.517323)], category='building')
    buildings = models.Fence.objects(polygon__geo_intersects=[float(request.args.get('lng')), float(request.args.get('lat'))], category='building')
    print len(buildings)
    data = {
        'outside' : len(buildings) == 0
    }

    response = Response(json.dumps(data), status=200, mimetype='application/json')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
