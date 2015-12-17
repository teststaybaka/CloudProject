from views import *

class MyServices(BaseHandler):
    @login_required
    def get(self):
        services = Service.query(Service.creator==self.user_key).order(-Service.created).fetch()
        self.render('serviceList', {'services': services})

class SearchServices(BaseHandler):
    def get(self):
        keywords = self.get_keywords()
        filters = []
        if keywords:
            filters.append('content: '+ keywords)
        
        status = self.request.get('status')
        if status:
            filters.append('status = '+status)

        price_min = self.request.get('price_min')
        if price_min:
            filters.append('price >= '+price_min)

        price_max = self.request.get('price_max')
        if price_max:
            filters.append('price <= '+price_max)

        kind = self.request.get('kind')
        if kind:
            filters.append('kind = '+kind)

        address = self.request.get('address')
        distance = self.request.get('distance')
        if address:
            try:
                loc_results = getGeolocation(address)
                latitude = loc_results[0]['geometry']['location']['lat']
                longitude = loc_results[0]['geometry']['location']['lng']
                t = float(distance)
            except ValueError:
                self.render('notify', {'message': 'Address or distance invalid.'})
                return

            filters.append('distance(location, geopoint('+str(latitude)+', '+str(longitude)+')) < '+distance)

        query_string = ' AND '.join(filters)
        options = search.QueryOptions(limit=20, ids_only=True)
        query = search.Query(query_string=query_string, options=options)
        index = search.Index(name='services_by_created')
        result = index.search(query)

        total_found = result.number_found
        services = ndb.get_multi([ndb.Key(urlsafe=doc.doc_id) for doc in result.results])
        creators = ndb.get_multi([service.creator for service in services])
        context = {'services': services, 'creators': creators, 'total_found': total_found}
        context.update({
            'keywords': keywords,
            'status': status,
            'price_min': price_min,
            'price_max': price_max,
            'kind': kind,
            'address': address,
            'distance': distance,
        })
        self.render('findService', context)

class ServiceHandle(BaseHandler):
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
        self.service_tags = list(set([tag.strip().lower() for tag in self.service_tags if tag.strip()]))
        if not self.service_tags:
            raise ValueError('No tags specified.')

        try:
            self.times = int(self.request.get('times'))
        except ValueError:
            self.times = 0
        
        self.kind = self.request.get('kind')
        if self.kind not in ["request", "offer"]:
            raise ValueError('Invalid kind.')

        self.address = self.request.get('address')
        if self.address:
            try:
                loc_results = getGeolocation(self.address)
                self.latitude = loc_results[0]['geometry']['location']['lat']
                self.longitude = loc_results[0]['geometry']['location']['lng']
                self.location = ndb.GeoPt(self.latitude, self.longitude)
            except ValueError:
                raise ValueError('Address invalid.')
        else:
            self.location = None

    @login_required_json
    def add_post(self):
        try:
            self.check_params()
        except ValueError as e:
            self.json_response(True, {'message': str(e)})
            return
        user = self.user_key.get()
        print user.tags
        user.tags = user.tags + self.service_tags
        user.put()
        print user.tags

        service = Service(creator=self.user_key, address=self.address, location=self.location, 
            title=self.title, description=self.description, price=self.price, available_time=self.available_time, 
            service_tags=self.service_tags, kind=self.kind)
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
    @login_required
    def get(self, service_id):
        service = ndb.Key('Service', int(service_id)).get()
        if not service:
            self.render('notify', {'message': 'Not existed.'})
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
