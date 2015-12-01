from google.appengine.ext import ndb
from google.appengine.api.datastore_errors import TransactionFailedError
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.api import search
from webapp2_extras.appengine.auth.models import Unique
from webapp2_extras import security
from google.appengine.ext import deferred
from datetime import datetime
import urllib2
import urlparse
import re
import logging
import math
import json

def time_to_seconds(time):
  return int((time - datetime(1970, 1, 1)).total_seconds())

EMAIL_REGEX = re.compile(r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")

class User(ndb.Model):
  Pepper = 'IcaAi1'

  lastname = ndb.StringProperty(required=True, indexed=False)
  firstname = ndb.StringProperty(required=True, indexed=False)
  gender = ndb.StringProperty(required=True, choices=['Male', 'Female'], indexed=False)
  auth_id = ndb.StringProperty()
  email = ndb.StringProperty(indexed=False)
  password = ndb.StringProperty(indexed=False)
  token = ndb.StringProperty()
  rates = ndb.FloatProperty()
  phone = ndb.StringProperty()

  @classmethod
  def Create(cls, lastname, firstname, gender, email, raw_password, phone):
    uniques = ['%s.%s:%s' % (cls.__name__, 'auth_id', email)]
    ok, existing = Unique.create_multi(uniques)
    if ok:
      password = security.generate_password_hash(raw_password, method='sha1', length=12, pepper=cls.Pepper)
      user = cls(auth_id=email, email=email, lastname=lastname, firstname=firstname, gender=gender, password=password, phone=phone)
      user.put()
      return user
    else:
      return None

  def auth_password(self, raw_password):
    return security.check_password_hash(raw_password, self.password, pepper=self.Pepper)

  @classmethod
  def get_user_with_password(cls, auth_id, password):
    user = cls.query(cls.auth_id==auth_id).get()
    if user and user.auth_password(password):
      return user
    else:
      return None

class Service(ndb.Model):
  creator = ndb.KeyProperty(kind='User', required=True)
  location = ndb.GeoPtProperty()
  description = ndb.TextProperty(indexed=False)
  price_min = ndb.IntegerProperty()
  price_max = ndb.IntegerProperty()
  available_time = ndb.StringProperty()
  service_type = ndb.StringProperty(required=True, choices=['Fashion', 'Beauty'])
  status = ndb.IntegerProperty(required=True, default=0)
