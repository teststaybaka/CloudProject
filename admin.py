from views import *

def remove_entites(entities):
    for e in entities:
        e.delete()

class Reset(BaseHandler):
    def get(self):
        remove_entites(User.query().fetch(keys_only=True))
        remove_entites(Service.query().fetch(keys_only=True))
        remove_entites(Proposal.query().fetch(keys_only=True))
        remove_entites(Message.query().fetch(keys_only=True))
        remove_entites(Unique.query().fetch(keys_only=True))
        self.json_response(False)
