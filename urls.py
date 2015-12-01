import webapp2
import views

routes = [
    webapp2.Route(r'/', views.Home, name="home"),
    webapp2.Route(r'/signup', views.Signup, name="signup"),
    webapp2.Route(r'/signin', views.Signin, name="signin"),
]
application = webapp2.WSGIApplication(routes, debug=True, config=config)
