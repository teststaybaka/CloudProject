from views import*

class MyProposals(BaseHandler):
    @login_required
    def get(self):
        proposals = Proposal.query(Proposal.requestor==self.user_key).order(-Proposal.created).fetch()
        self.render('myrequests', {'proposals': proposals})

class ReceivedProposals(BaseHandler):
    @login_required
    def get(self):
        proposals = Proposal.query(Proposal.decider==self.user_key).order(-Proposal.created).fetch()
        self.render('myreceives', {'receives': proposals})

class Propose(BaseHandler):
    @login_required
    def get(self, service_id):
        service = ndb.Key('Service', int(service_id)).get()
        if not service or service.status != 'available' or service.creator == self.user_key:
            self.render('notify', {'message': 'Not allowed.'})
            return

        self.render('propose', {'service': service})
        
    @login_required_json
    def post(self, service_id):
        service = ndb.Key('Service', int(service_id)).get()
        if not service or service.status != 'available' or service.creator == self.user_key:
            self.json_response(True, {'message': 'Not allowed.'})
            return

        try:
            times = int(self.request.get('times'))
        except ValueError:
            self.json_response(True, {'message': 'Invalid times.'})
            return

        try:
            price = int(self.request.get('price'))
        except ValueError:
            price = 0

        proposal = Proposal(decider=service.creator, requestor=self.user_key, service=service.key, kind=service.kind, price=price, times=times)
        proposal.put()

        text = 'Hi '+service.creator.get().firstname+',\n'
        text += self.user_key.get().firstname+'is requesting to '
        if service.kind == 'offer':
            text += 'take your service. '
        else:
            text += 'offer you a service. '
        text += 'Are you interested?'
        message = Message(parent=proposal.key, sender=self.user_key, receiver=service.creator, text=text)
        proposal.last_message = text
        ndb.put_multi((message, proposal))
        self.json_response(False)

class Conversation(BaseHandler):
    @login_required
    def get(self, proposal_id):
        proposal = ndb.Key('Proposal', int(proposal_id)).get()
        if not proposal or (self.user_key != proposal.decider and self.user_key != proposal.requestor):
            self.redirect(self.render('notify', {'message': 'Not allowed.'}))
            return

        messages = Message.query(ancestor=proposal.key).order(-Message.created).fetch()
        self.render('messages', {'messages': messages, 'proposal': proposal, 'service': proposal.service.get()})

    @login_required_json
    def send(self, proposal_id):
        proposal = ndb.Key('Proposal', int(proposal_id)).get()
        if not proposal:
            self.json_response(True, {'message': 'Not existed'})
            return

        if self.user_key == proposal.decider:
            receiver = proposal.requestor
        elif self.user_key == proposal.requestor:
            receiver = proposal.decider
        else:
            self.json_response(True, {'message': 'Not allowed.'})
            return

        text = self.request.get('message')
        message = Message(parent=proposal.key, sender=self.user_key, receiver=receiver, text=text)
        proposal.last_message = text
        ndb.put_multi((message, proposal))
        self.json_response(False)

    @login_required_json
    def modify(self, proposal_id):
        proposal = ndb.Key('Proposal', int(proposal_id)).get()
        if not proposal or proposal.requestor != self.user_key or proposal.status != 'pending':
            self.json_response(True, {'message': 'Not allowed.'})
            return

        try:
            times = int(self.request.get('times'))
        except ValueError:
            self.json_response(True, {'message': 'Invalid times.'})
            return

        try:
            price = int(self.request.get('price'))
        except ValueError:
            price = 0

        proposal.times = times
        proposal.price = price
        text = 'The proposal has been modified. Please check it!'
        message = Message(parent=proposal.key, sender=self.user_key, receiver=proposal.decider, text=text)
        proposal.last_message = text
        ndb.put_multi((message, proposal))
        self.json_response(False)

class DeclineProposal(BaseHandler):
    @login_required_json
    def post(self, proposal_id):
        proposal = ndb.Key('Proposal', int(proposal_id)).get()
        if not proposal or proposal.decider != self.user_key or proposal.status != 'pending':
            self.json_response(True, {'message': 'Not allowed.'})
            return

        proposal.status = 'declined'
        proposal.put()
        self.json_response(False)

class AcceptProposal(BaseHandler):
    @login_required_json
    def post(self, proposal_id):
        proposal = ndb.Key('Proposal', int(proposal_id)).get()
        if not proposal or proposal.decider != self.user_key or proposal.status != 'pending':
            self.json_response(True, {'message': 'Not allowed.'})
            return

        service = proposal.service.get()
        if service.status != 'available':
            self.json_response(True, {'message': 'Not available.'})
            return

        proposal.status = 'accepted'
        service.status = 'handling'
        ndb.put_multi((service, proposal))
        self.json_response(False)

class Progress(BaseHandler):
    @login_required_json
    def post(self, proposal_id):
        proposal = ndb.Key('Proposal', int(proposal_id)).get()
        if not proposal or proposal.status != 'accepted' or proposal.decider != self.user_key or proposal.progress >= proposal.times:
            self.json_response(True, {'message': 'Invalid request.'})
            return

        proposal.progress += 1
        if proposal.progress == proposal.times:
            proposal.status = 'finished'
        proposal.put()
        self.json_response(False)

class ConfirmProgress(BaseHandler):
    @login_required_json
    def post(self, proposal_id):
        proposal = ndb.Key('Proposal', int(proposal_id)).get()
        if not proposal or proposal.status != 'accepted' or proposal.requestor != self.user_key or proposal.progress >= proposal.confirmed_progress:
            self.json_response(True, {'message': 'Invalid request.'})
            return

        proposal.confirmed_progress = proposal.progress
        if proposal.progress == progress.times:
            proposal.status = 'confirmed'
        proposal.put()
        self.json_response(False)
