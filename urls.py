import webapp2
import views, service, propose

routes = [
    webapp2.Route(r'/', views.Home, name="home"),
    webapp2.Route(r'/signup', views.Signup, name="signup"),
    webapp2.Route(r'/signin', views.Signin, name="signin"),
    webapp2.Route(r'/signout', views.Signout, name="signout"),
    
    webapp2.Route(r'/my/services', service.MyServices, name="my_services"),
    webapp2.Route(r'/search', service.SearchServices, name="search_services"),
    webapp2.Route(r'/service/add', service.ServiceHandle, name="add_service", handler_method='add'),
    webapp2.Route(r'/service/add/post', service.ServiceHandle, name="add_service_post", handler_method='add_post'),
    webapp2.Route(r'/service/<service_id:\d+>/modify', service.ServiceHandle, name="modify_service", handler_method='modify'),
    webapp2.Route(r'/service/<service_id:\d+>/modify/post', service.ServiceHandle, name="modify_service_post", handler_method='modify_post'),
    webapp2.Route(r'/service/<service_id:\d+>', service.ServiceDetail, name="service_detail"),
    webapp2.Route(r'/service/<service_id:\d+>/cancel', service.CancelService, name="cancel_service"),

    webapp2.Route(r'/my/proposal', propose.MyProposals, name="my_proposal"),
    webapp2.Route(r'/my/receives', propose.ReceivedProposals, name="my_receives"),
    webapp2.Route(r'/service/<service_id:\d+>/propose', propose.Propose, name="propose"),
    webapp2.Route(r'/proposal/<proposal_id:\d+>', propose.Conversation, name="proposal"),
    webapp2.Route(r'/proposal/<proposal_id:\d+>/send', propose.Conversation, name="send_message", handler_method='send'),
    webapp2.Route(r'/proposal/<proposal_id:\d+>/modify', propose.Conversation, name="modify_proposal", handler_method='modify'),
    webapp2.Route(r'/proposal/<proposal_id:\d+>/decline', propose.DeclineProposal, name="decline_proposal"),
    webapp2.Route(r'/proposal/<proposal_id:\d+>/accept', propose.AcceptProposal, name="accept_proposal"),
    webapp2.Route(r'/proposal/<proposal_id:\d+>/progress', propose.Progress, name="progress"),
    webapp2.Route(r'/proposal/<proposal_id:\d+>/finish', propose.FinishProposal, name="finish_proposal"),
    webapp2.Route(r'/proposal/<proposal_id:\d+>/confirm', propose.ConfirmFinish, name="confirm_proposal"),
]
application = webapp2.WSGIApplication(routes, debug=True)
