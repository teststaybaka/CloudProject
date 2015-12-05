#Make Get request to FB
import requests

#Used to verify our app integrity
FBSECRET = "cabf97c715e4127b197193aee8f9f801" 
FBAPPID = "441962862657459"

def fb_get_user_id(access_token):
	'''Facebook access token reverification

	Makes connection to graph and verifies token
	integrity
	'''

	r = requests.get("graph.facebook.com/debug_token?"
					+"input_token="+access_token
					+"&amp;access_token="+FBSECRET)

	fb = r.json()

	if fb.data.app_id == FBAPPID and fb.data.is_valid:
		return fb.data.user_id

	return None


