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
ILLEGAL_LETTER = re.compile(r"[&@.,?!:/\\\"'<>=]")

class User(ndb.Model):
  Pepper = 'IcaAi1'

  lastname = ndb.StringProperty(required=True, indexed=False)
  firstname = ndb.StringProperty(required=True, indexed=False)
  gender = ndb.StringProperty(required=True, indexed=False)
  auth_id = ndb.StringProperty()
  # location = ndb.GeoPtProperty(indexed=False)
  email = ndb.StringProperty(indexed=False)
  password = ndb.StringProperty(indexed=False)
  rates = ndb.FloatProperty(indexed=False)
  phone = ndb.StringProperty(indexed=False)

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

  @classmethod
  def get_user_with_uid(cls, auth_id):
    user = cls.query(cls.auth_id==auth_id).get()
    if user:
      return user
    else:
      return None

# SERVICE_TYPES = ['Nails', 'Tutoring', 'Babysitting', 'Fashion', 'Beauty', 'Housing', 'Housekeeping', 'Designated driving']
class Service(ndb.Model):
  creator = ndb.KeyProperty(kind='User', required=True)
  address = ndb.StringProperty(indexed=False)
  location = ndb.GeoPtProperty(indexed=False)
  title = ndb.StringProperty(indexed=False)
  description = ndb.TextProperty(indexed=False)
  price = ndb.IntegerProperty(indexed=False)
  times = ndb.IntegerProperty(required=True, default=1, indexed=False)
  available_time = ndb.StringProperty(indexed=False)
  service_tags = ndb.StringProperty(repeated=True, indexed=False)
  status = ndb.StringProperty(required=True, default='available', choices=['available', 'handling', 'cancelled', 'completed'])
  kind = ndb.StringProperty(required=True, choices=['offer', 'request'])
  # rates = ndb.FloatProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)

  def createIndex(self):
    index = search.Index(name='services_by_created')
    searchable = " ".join(self.service_tags+[self.description]);
    fields = [
        search.TextField(name='content', value=searchable.lower()),
        search.NumberField(name='price', value=self.price),
        search.AtomField(name='status', value=self.status),
    ]
    if self.address:
        fields.append(search.GeoField(name='location', value=search.GeoPoint(self.location.latitude, self.location.longitude)))
    
    doc = search.Document(
        doc_id = self.key.urlsafe(), 
        fields = fields,
        rank = time_to_seconds(self.created),
    )
    index.put(doc)

class Proposal(ndb.Model):
  decider = ndb.KeyProperty(kind='User')
  requestor = ndb.KeyProperty(kind='User')
  service = ndb.KeyProperty(kind='Service')
  times = ndb.IntegerProperty(indexed=False)
  price = ndb.IntegerProperty(indexed=False)
  progress = ndb.IntegerProperty(required=True, default=0, indexed=False)
  status = ndb.StringProperty(required=True, default='pending', choices=['pending', 'accepted', 'declined', 'finished', 'confirmed'])
  last_message = ndb.TextProperty()
  kind = ndb.StringProperty(required=True, choices=['offer', 'request'])
  created = ndb.DateTimeProperty(auto_now_add=True)

class Message(ndb.Model):
  sender = ndb.KeyProperty(kind='User', indexed=False)
  receiver = ndb.KeyProperty(kind='User', indexed=False)
  text = ndb.TextProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)
