import os
import glob
from datetime import datetime
from behave import parser as behave_parser
from behave import model as behave_models
from habitat import app
import utils
import models
import forms
from flask import Flask, request, redirect, render_template, json, Response, url_for, flash, session, abort

@app.route("/")
def scenarios():

    features = []
    for feature_file_path in glob.glob(app.config['FEATURE_DIR'] + '/*.feature'):

        feature = behave_parser.parse_file(feature_file_path)
        feature_id = os.path.basename(feature_file_path).split('.')[0]
        modified_at = datetime.fromtimestamp(os.path.getmtime(feature_file_path))

        features.append({'code': utils.feature_to_string(feature), 'modified_at': modified_at, 'feature_id': feature_id})

    return render_template('scenarios.html', features=features)

@app.route("/scenarios/<scenario_id>", methods=['GET', 'POST'])
def edit(scenario_id):

    form = forms.ScenarioForm(request.form)
    if request.method == 'GET':
        if scenario_id != 'new':
            feature_file_path = utils.get_feature_file_name(scenario_id)
            feature = behave_parser.parse_file(feature_file_path)
            form.code.data = utils.feature_to_string(feature)
        else:
            form.code.data = ''

    if request.method == 'POST' and form.validate():
        
        feature = behave_parser.parse_feature(form.code.data)

        feature_file_path = utils.get_feature_file_name(scenario_id)
        if scenario_id == 'new':
            feature_file_path = utils.get_feature_file_name(utils.generate_feature_file_name(feature))

        file_ref = open(feature_file_path, 'w')
        file_ref.write(utils.feature_to_string(feature))
        return redirect(url_for('scenarios'))

    return render_template('edit.html', form=form)

@app.route("/settings")
def settings():
    return render_template('settings.html')

# @app.route("/api/")
# def api():
#     #building: http://localhost:5000/api/?lng=-0.1206612&lat=51.517323
#     #road: http://localhost:5000/api/?lng=-0.120442&lat=51.517546
#     #buildings = models.Fence.objects(polygon__geo_intersects=[float(-0.1206612), float(51.517323)], category='building')
#     buildings = models.Fence.objects(polygon__geo_intersects=[float(request.args.get('lng')), float(request.args.get('lat'))], category='building')
#     print len(buildings)
#     data = {
#         'outside' : len(buildings) == 0
#     }

#     response = Response(json.dumps(data), status=200, mimetype='application/json')
#     return response
