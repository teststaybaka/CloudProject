#JSON Array is passed
import json

#Make Get request to FB
import urllib2
import logging

#Used to verify our app integrity
FBSECRET = "cabf97c715e4127b197193aee8f9f801" 
FBAPPID = "441962862657459"

def fb_get_user_id(access_token):
	'''Facebook access token reverification

	Makes connection to graph and verifies token
	integrity
	'''

	r = urllib2.urlopen("https://graph.facebook.com/me?access_token="
					+access_token)
	
	fb = json.load(r)

	try:
		return fb['id']
	except KeyError:
		return None



