from views import *

class MyServices(BaseHandler):
    @login_required
    def get(self):
        services = Service.query(Service.creator==self.user_key).order(-Service.created).fetch()
        self.render('serviceList', {'services': services})

class SearchServices(BaseHandler):
    def get(self):
        self.render('findService')

    def post(self):
        keywords = self.get_keywords()
        query_string = 'content: '+keywords

        status = self.request.get('status')
        if status:
            query_string += ' AND status = '+status

        price_min = self.request.get('price_min')
        if price_min:
            query_string += ' AND price >= '+price_min

        price_max = self.request.get('price_max')
        if price_max:
            query_string += ' AND price <= '+price_max

        address = self.request.get('address')
        if address:
            try:
                latitude = self.request.get('latitude')
                longitude = self.request.get('longitude')
                distance = self.request.get('distance')
                t = float(latitude)
                t = float(longitude)
                t = float(distance)
            except ValueError:
                self.redirect(self.render('notify', {'message': 'Latitude, longitude or distance invalid.'}))
                return

            query_string += ' AND distance(location, geopoint('+latitude+', '+longitude+')) < '+distance

        options = search.QueryOptions(limit=20, ids_only=True)
        query = search.Query(query_string=query_string, options=options)
        index = search.Index(name='services_by_created')
        result = index.search(query)

        total_found = result.number_found
        services = ndb.get_multi([ndb.Key(urlsafe=doc.doc_id) for doc in result.results])
        creators = ndb.get_multi([service.creator for service in services])
        self.render('findResult', {'services': services, 'creators': creators})

class Service(BaseHandler):
    @login_required
    def add(self):
        self.render('serviceAdd')

    @login_required
    def modify(self, service_id):
        service = ndb.Key('Service', int(service_id)).get()
        if not service or service.creator != self.user_key or service.status != 'available':
            self.render('notify', {'message': 'Not allowed.'})
            return

        self.render('serviceModify', {'service': service})

    def check_params(self):
        self.address = self.request.get('address')
        if self.address:
            try:
                self.latitude = float(self.request.get('latitude'))
                self.longitude = float(self.request.get('longitude'))
                self.location = ndb.GeoPt(self.latitude, self.longitude)
            except ValueError:
                raise ValueError('Latitude or longitude not valid.')
        else:
            self.location = None

        self.title = self.request.get('title')
        if not self.title:
            raise ValueError('Title is empty.')

        self.description = self.request.get('description')
        if not self.description:
            raise ValueError('Description is empty.')

        try:
            self.price = int(self.request.get('price'))
        except ValueError:
            self.price = 0

        self.available_time = self.request.get('available_time')
        if not self.available_time:
            raise ValueError('Not specify available time.')

        self.service_tags = self.request.get('service_tags').split(",")
        if not self.service_tags:
            raise ValueError('No tags specified.')

        try:
            self.times = self.request.get('times')
        except ValueError:
            raise ValueError('Invalid times.')

    @login_required_json
    def add_post(self):
        try:
            self.check_params()
        except ValueError as e:
            self.json_response(True, {'message': str(e)})
            return

        service = Service(creator=self.user_key, address=self.address, location=self.location, title=self.title, description=self.description, price=self.price, available_time=self.available_time, service_tags=self.service_tags)
        service.put()
        service.createIndex()
        self.json_response(False)

    @login_required_json
    def modify_post(self, service_id):
        try:
            self.check_params()
        except ValueError as e:
            self.json_response(True, {'message': str(e)})
            return

        service = ndb.Key('Service', int(service_id)).get()
        if not service or service.status != 'available' or service.creator != self.user_key:
            self.json_response(True, {'message': 'Invalid modification.'})
            return

        service.address = self.address
        service.location = self.location
        service.description = self.description
        service.price = self.price
        service.available_time = self.available_time
        service.service_tags = self.service_tags
        service.put()
        service.createIndex()
        self.json_response(False)

class ServiceDetail(BaseHandler):
    def get(self, service_id):
        service = ndb.Key('Service', int(service_id)).get()
        if not service:
            self.redirect(self.render('notify', {'message': 'Not existed.'}))
            return

        self.render('serviceDetail', {'service': service, 'creator': service.creator.get()})

class CancelService(BaseHandler):
    @login_required_json
    def post(self, service_id):
        service = ndb.Key('Service', int(service_id)).get()
        if not service or service.status != 'available' or service.creator != self.user_key:
            self.json_response(True, {'message': 'Invalid cancellation.'})
            return

        service.status = 'cancelled'
        service.put()
        self.json_response(False)
