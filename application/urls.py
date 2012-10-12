"""
urls.py

contains all of the routes and the view/action handlers.
also declares a decorator and some other things.

"""

from application import app
from flask import request, redirect, url_for, render_template
from functools import wraps
import httplib2
import os
import md5
import json
import logging

from application.settings import REQUEST_SCOPE, RETURN_URL
from application.models import AlbumEmailMapping, UserCredential, AlbumList


from oauth2client.client import flow_from_clientsecrets
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import db

def login_required(func):
    """Requires standard login credentials"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.get_current_user():
            return redirect(users.create_login_url(request.url))
        return func(*args, **kwargs)
    return decorated_view

@app.route('/')
def home():
    user = users.get_current_user()
    credentials = None
    mappings = None
    if user:
        credentials = UserCredential.get_by_user(user)
        mappings = AlbumEmailMapping.all().filter('owner =', user)
        
    return render_template('home.html', user=user, credentials=credentials, 
                           mappings=mappings)
    
@app.route('/login')
@login_required
def login():
    return redirect(url_for('home'))
    
@app.route('/auth')
@login_required
def start_auth():
    if 'new' in request.args:
        # delete existing credential stores.
        memcache.delete()
    if 'new' not in request.args:
        # check for pre-existing auth
        credentials = UserCredential.get_by_user(users.get_current_user())
        if credentials:
            return redirect(url_for('list_albums'))
        
    # generate a flow to authenticate the user.
    flow = flow_from_clientsecrets('client_secrets.json', 
                                   scope=REQUEST_SCOPE, 
                                   redirect_uri=RETURN_URL)
    auth_url = str(flow.step1_get_authorize_url())
    logging.info('auth url: %s' % auth_url)
    
    # stash flow
    memcache.set('flow:%s' % users.get_current_user().user_id(), flow)
    return redirect(auth_url)
    
@app.route('/auth/auth_return')
@login_required
def finish_auth():
    if 'error' in request.args:
        return 'You must grant access for this to work, silly'
    
    if 'code' in request.args:
        # auth success, retrieve flow then build and stash credentials.
        flow = memcache.get('flow:%s' % users.get_current_user().user_id())
        credentials = flow.step2_exchange(request.args['code'])
        UserCredential.set_credentials_for_user(users.get_current_user(), 
                                                credentials)
        
    return redirect(url_for('home'))
    
@app.route('/albums')
@login_required
def list_albums():
    user = users.get_current_user()
    if 'refresh' in request.args:
        AlbumList.delete_for_user(user)
        return redirect(url_for('list_albums'))
    album_list = AlbumList.get_for_user(user)
    
    album_mappings = dict() # key=albumid, value=mapping
    for mapping in AlbumEmailMapping.all().filter('owner =', user):
        # this is a mapping.  
        album_id = mapping.album['gphoto$id']['$t']
        logging.info('adding album with id %s to map.' % album_id)
        album_mappings[album_id] = mapping
    return render_template('albums.html', user=user, album_list=album_list, 
                           album_mappings=album_mappings)
    
@app.route('/albums/<album_id>')
def select_album(album_id):
    user = users.get_current_user()
    album_list = AlbumList.get_for_user(user)
    the_album = None
    for album in album_list:
        if album['gphoto$id']['$t'] == album_id:
            the_album = album
            break
                    
    if not album:
        return 'album not found'
        
    email_address = md5.new(os.urandom(25)).hexdigest()
    # if it's taken, generate new
    while AlbumEmailMapping.all().filter('email_address = ', email_address) \
                           .count() > 0:
        email_address = md5.new(os.urandom(25)).hexdigest()
        
    mapping = AlbumEmailMapping(
        owner=user,
        email_address=email_address,
        album=album)
        
    mapping.put()
    return redirect(url_for('list_albums'))