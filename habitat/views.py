from flask import render_template
from habitat import app

@app.route('/')
def hello():
    #https://www.flickr.com/photos/54459164@N00/13134244664/
    return render_template('index.html')
