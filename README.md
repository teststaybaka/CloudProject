# CloudProject
### App Engine Project ID:
hands-for-you  

### URL:
http://hands-for-you.appspot.com/  

### Local start:
dev_appserver.py CloudProject  
Note: CloudProject here is the folder name of your local copy of the codes. So execute the command just outside the folder.  
Also, you don't need to restart the local server when you make changes to files. Simply refresh the page will reload the code.

### Local url:
http://localhost:8080  

### Local app engine admin console:
http://localhost:8000  

### Remote deploy:
appcfg.py update CloudProject  

### Remove index:
appcfg.py vacuum_indexes CloudProject  

### Prerequisites:
[Google App Engine SDK](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python)  
You may need [Google Cloud SDK](https://cloud.google.com/sdk/?hl=en#windows) to deploy remotely and run "gcloud init". Unfortunately, I can't recall details for the authentication process. I guess "gcloud init" should be enough. If not, check [more documents](https://cloud.google.com/sdk/gcloud/).  

### Application entrance:
urls.py which defines the mapping from url to handlers  

### User related handlers:
views.py contains handlers for all user related request including sign in, sign up, home page and user settings.  

### Service related handlers:
service.py contains handlers for services including creating service, modifying service, displaying service creation hsitory, searching services and service details.  

### Proposal related handlers:
propose.py includes proposal history, creating proposal, modifying proposal, sending message, accepting/declining proposal, making progress and confirmation.

### Template engine:
[Jinja2](http://jinja.pocoo.org/docs/dev/templates/) is used to render html pages and base.html is the base of all html files, meaning same headers/html blocks that are reused through other html files should be written in base.html. Put all template html files in /template folder.  

### Model definition:
models.py which defines the models using [NDB datastore API](https://cloud.google.com/appengine/docs/python/ndb/).  

### Static files:
Put all static files in /static folder (except for templates) and access by "/static/*".  

### Message server:
`/Messages` contains the code deployed in Google Compute Engine which is a websocket server for real-time messaging.  
