# CloudProject
## App Engine Project ID:
hands-for-you  

### URL:
http://hands-for-you.appspot.com/  

### Local start:
dev_appserver.py CloudProject  
Note: CloudProject here is the folder name of your local copy of the codes. So execute the command just outside the folder.  

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

### Main handlers:
views.py which handles the response. Jinja2 template engine is used to render html files.  

### Template engine:
[Jinja2](http://jinja.pocoo.org/docs/dev/templates/), with which base.html can be used as the base of all html files, meaning same headers/html blocks that are reused through other html files should be written in base.html. Put all template html files in /template folder.  

### Model definition:
models.py which defines the models using [NDB datastore API](https://cloud.google.com/appengine/docs/python/ndb/).  

### Static files:
Put all static files in /static folder (except for templates) and access by "/static/*".  
