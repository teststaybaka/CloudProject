import jinja2
import os
import traceback
import webapp2
import cStringIO
import itertools
import mimetools
import mimetypes
import random
import cgi
import collections
import base64

from google.appengine.api import app_identity
from datetime import datetime
from jinja2 import Undefined
from google.appengine.api.datastore_errors import BadValueError
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import mail
from auth import fb_get_user_id

from models import *

class SilentUndefined(Undefined):
    '''
    Dont break pageloads because vars arent there!
    '''
    def _fail_with_undefined_error(self, *args, **kwargs):
        logging.exception('JINJA2: something was undefined!')
        return None

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
    undefined=SilentUndefined)
env.globals = {
    'uri_for': webapp2.uri_for,
}

class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def user_key(self):
        u = self.request.cookies.get('user_id')
        if u:
            try:
                return ndb.Key('User', int(u))
            except ValueError:
                return None
        else:
            return None

    def get_keywords(self):
        return ILLEGAL_LETTER.sub(' ', self.request.get('keywords')).strip().lower()

    def render(self, tempname, context=None):
        if not context:
            context = {}

        if self.user_key:
            if 'user' not in context:
                context['user'] = self.user_key.get()

        self.response.headers['Content-Type'] = 'text/html'
        path = 'template/' + tempname + '.html'
        template = env.get_template(path)
        self.response.write(template.render(context))
        
    def json_response(self, error, result={}):
        self.response.headers['Content-Type'] = 'application/json'
        result['error'] = error
        self.response.write(json.dumps(result))

def login_required(handler):
    def check_login(self, *args, **kwargs):
        if not self.user_key:
            self.redirect(self.uri_for('signin'))
        else:
            return handler(self, *args, **kwargs)
 
    return check_login

def login_required_json(handler):
    def check_login(self, *args, **kwargs):
        if not self.user_key:
            self.json_response(True, {'message': 'Please log in!'})
        else:
            return handler(self, *args, **kwargs)
 
    return check_login

class Home(BaseHandler):
    def get(self):
        
        if self.user_key:
            user = self.user_key.get()
            logging.info(user.tags)
            if user.tags:
                all_service_with_those_tags = Service.query(Service.creator!=self.user_key, Service.status == "available", Service.service_tags.IN(user.tags)).order(Service.creator, -Service.created).fetch()
            else:
                all_service_with_those_tags = Service.query(Service.creator!=self.user_key, Service.status == "available").order(Service.creator, -Service.created).fetch()
        else:
            all_service_with_those_tags = Service.query(Service.status == "available").order(-Service.created).fetch()
        
        non_rep=[]
        for i in range(0,len(all_service_with_those_tags)):
            curr=all_service_with_those_tags[i]
            if i>0:
                prev=all_service_with_those_tags[i-1]
                if curr!=prev:
                    non_rep+=[curr]
            else:
                non_rep+=[curr]

        self.render('index2',{'services':non_rep})

class Signup(BaseHandler):
    def post(self):
        if self.user_key:
            self.json_response(True, {'message': 'Already sign in!'})
            return

        email = self.request.get('email')
        password = self.request.get('password')
        lastname = self.request.get('lastname')
        firstname = self.request.get('firstname')
        gender = self.request.get('gender')
        phone = self.request.get('phone')

        if not firstname:
            self.json_response(True, {'message': 'Firstname is empty.'})
            return

        if not lastname:
            self.json_response(True, {'message': 'Lastname is empty.'})
            return

        if not EMAIL_REGEX.match(email):
            self.json_response(True, {'message': 'Email format invalid.'})
            return

        if not password:
            self.json_response(True, {'message': 'Password is empty.'})
            return

        if gender not in ['Male', 'Female']:
            self.json_response(True, {'message': 'Gender invalid.'})
            return

        user = User.Create(lastname=lastname, firstname=firstname, gender=gender, email=email, raw_password=password, phone=phone)
        if not user:
            self.json_response(True, {'message': 'Create user failed.'})
            return

        self.response.set_cookie('user_id', str(user.key.id()), path='/')
        self.json_response(False)

class Signin(BaseHandler):
    def get(self):
        if self.user_key:
            self.redirect(self.uri_for('home'))
        else:
            self.render('signin')

    def post(self):
        if self.user_key:
            self.json_response(True, {'message': 'Already sign in!'})
            return

        access_token = self.request.get('fb-access-token')
        if access_token:
            try:
                uid = fb_get_user_id(access_token)
            except Exception:
                self.json_response(True, {'message': 'Facebook login failed.'})
                return

            if uid:
                user = User.get_user_with_uid(uid)
                if not user:
                    firstname = self.request.get('firstname')
                    lastname = self.request.get('lastname')
                    gender = self.request.get('gender')
                    email = self.request.get('email')

                    user = User(auth_id=uid, email=email, firstname=firstname, lastname=lastname, gender=gender)
                    user.put()
            else:
                self.json_response(True, {'message': 'Facebook login failed.'})
                return

        else:
            email = self.request.get('email')
            password = self.request.get('password')
            user = User.get_user_with_password(email, password)

            if not user:
                self.json_response(True, {'message': 'Email and password don\'t match.'})
                return

        self.response.set_cookie('user_id', str(user.key.id()), path='/')
        self.json_response(False)
        
class Signout(BaseHandler):
    @login_required
    def get(self):
        self.response.set_cookie('user_id', '', path='/', max_age=0)
        self.redirect(self.uri_for('home'))
        
class Account(BaseHandler):
    @login_required
    def get(self):
        self.render('account_setting')

    @login_required_json
    def post(self):
        email = self.request.get('email')
        phone = self.request.get('phone')
        address = self.request.get('address')
        distance = self.request.get('distance')
        tags = self.request.get('tags').split(',')
        tags = list(set([tag.strip().lower() for tag in tags if tag.strip()]))

        if not EMAIL_REGEX.match(email):
            self.json_response(True, {'message': 'Email format invalid.'})
            return

        if address:
            try:
                loc_results = getGeolocation(address)
                latitude = loc_results[0]['geometry']['location']['lat']
                longitude = loc_results[0]['geometry']['location']['lng']
                distance = float(distance)
                location = ndb.GeoPt(latitude, longitude)
            except ValueError:
                self.json_response(True, {'message': 'Address or distance invalid.'})
                return
        else:
            location = None
            distance = None

        user = self.user_key.get()
        user.email = email
        user.phone = phone
        user.address = address
        user.distance = distance
        user.location = location
        user.tags = tags
        user.put()
        self.json_response(False)