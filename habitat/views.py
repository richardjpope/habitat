from flask import render_template, request, redirect, url_for, session
from habitat import app, oauth
from models import AuthClient, AuthToken
from mongoengine import DoesNotExist
import auth
from decorators import admin_login_required
import forms

@app.route('/')
@admin_login_required
def hello():

    #https://www.flickr.com/photos/54459164@N00/13134244664/
    #https://www.flickr.com/photos/superlekker/2298343199/
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def admin_login():
    form = forms.AdminLoginForm(request.form)
    failed=False
    if request.method == 'POST' and form.validate():
        if app.config['ADMIN_USERNAME'] == form.data['username'] and app.config['ADMIN_PASSWORD'] == form.data['password']:
            session['admin'] = True
            return redirect(url_for('hello'))
        else:
            failed=True

    return render_template('login.html', form=form, failed=failed)

@app.route('/signout')
def admin_logout():
    session.clear()
    return redirect(url_for('hello'))

@app.route('/settings', methods=['GET', 'POST'])
@admin_login_required
def authorized():
    if request.method == 'POST':
        token = AuthToken.objects.get(id=request.form['revoke'])
        token.delete()
        #todo: delete client if no outstanding tokens

    tokens = AuthToken.objects()
    return render_template('authorized.html', tokens=tokens)

@app.route('/oauth/token')
@oauth.token_handler
def access_token():
    return None

@app.route('/oauth/authorize', methods=['GET', 'POST'])
@admin_login_required
@auth.pre_authorize_handler
@oauth.authorize_handler
def authorize(*args, **kwargs):

    if request.method == 'GET':
        client = None
        client = AuthClient.objects.get(client_id=request.args.get('client_id'))
        client_id = client.client_id
        client = AuthClient.objects.get(client_id=client_id)
        kwargs['client'] = client

        return render_template('authorize.html', avaliable_scopes=auth.scopes, **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'
