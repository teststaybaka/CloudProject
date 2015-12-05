import webapp2
import views

routes = [
    webapp2.Route(r'/', views.Home, name="home"),
    webapp2.Route(r'/signup', views.Signup, name="signup"),
    webapp2.Route(r'/signin', views.Signin, name="signin"),
    webapp2.Route(r'/signout', views.Signout, name="signout"),
    webapp2.Route(r'/service/add', views.AddService, name="add_service"),
    webapp2.Route(r'/services/<service_id:\d+>', views.ServiceDetail, name="my_services"),
]
application = webapp2.WSGIApplication(routes, debug=True)
