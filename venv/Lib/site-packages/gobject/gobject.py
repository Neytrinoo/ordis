'''gobject.py'''

import json

from .exception import Status, UnsupportedDataTypeError


def load(data):
    '''Transform Google Geocode API JSON response into Gobject.

    This operation is reversable using serialize() function, or through
    gobject_instance.serialize() API method.

    Returns:
        Gobject instance initialized with data
    '''
    return Gobject(data)


def serialize(obj):
    '''Transform Gobject instance into Google Geocode JSON response.

    Returns:
        Serialized object to dictionary
    '''
    return Gobject.serialize()


class Location(object):
    def __init__(self, coordinates):
        self.lat = coordinates['lat']
        self.lng = coordinates['lng']

    def __repr__(self):
        return '<lat: {0} ; lng: {1}>'.format(self.lat, self.lng)

    def __eq__(self, other):
        lat_diff = (self.lat == other.lat)
        lng_diff = (self.lng == other.lng)

        if (lat_diff and lng_diff):
            return True
        else:
            return False

    def __dict__(self):
        return {'lat': self.lat, 'lng': self.lng}


class AddressComponent(object):
    def __init__(self, long_name, short_name, types):
        self.long_name = long_name
        self.short_name = short_name
        self.types = types

    def __repr__(self):
        return '<long name: {0}, short name: {1}, types: {2}>'.format(
            self.long_name, self.short_name, self.types)

    def __eq__(self, other):
        long_name_diff = (self.long_name == other.long_name)
        short_name_diff = (self.short_name == other.short_name)
        types_diff = (self.types == other.types)

        if (long_name_diff and short_name_diff and types_diff):
            return True
        else:
            return False

    def __dict__(self):
        return {
            'long_name': self.long_name,
            'short_name': self.short_name,
            'types': self.types
        }


class GeoPair(object):
    '''Wraps two named coordinate pairs.

    Bounds and viewport is essentially one data structure with different names.
    This data holds two coordinates: northeas and southwest.
    '''

    def __init__(self, northeast, southwest):
        self.northeast = Location(northeast)
        self.southwest = Location(southwest)

    def __repr__(self):
        return '<northeast: {0}, southwest: {1}>'.format(self.northeast,
                                                         self.southwest)

    def __eq__(self, other):
        ne_diff = (self.northeast == other.northeast)
        sw_diff = (self.southwest == other.southwest)

        if (ne_diff and sw_diff):
            return True
        else:
            return False

    def __dict__(self):
        return {
            'northeast': self.northeast.__dict__(),
            'southwest': self.southwest.__dict__()
        }


class Gobject(object):
    def __init__(self, data):
        '''Google Geocode API wrapper.

        Args:
            data: google geoservice API response in form of JSON string or object
        '''

        if (data.__class__ != {}.__class__ and data.__class__ != ''.__class__):
            raise UnsupportedDataTypeError(
                'Provided data type {0} is unsupported'.format(type(data)))

        geo = self._load_data(data)

        self._check_status(geo['status'])

        geo = geo['results'][0]

        self.address_components = self._parse_addr(geo['address_components'])
        self.formatted_address = geo['formatted_address']
        self.bounds = self._parse_geopair(geo['geometry']['bounds'])
        self.location = self._parse_location(geo['geometry']['location'])
        self.viewport = self._parse_geopair(geo['geometry']['viewport'])
        self.location_type = geo['geometry']['location_type']
        self.place_id = geo['place_id']
        self.types = geo['types']

    def _load_data(self, data):
        if (type(data) == {}.__class__):
            return data
        elif (type(data) == ''.__class__):
            return json.loads(data)

    def _check_status(self, status):
        if status != Status.OK.name:
            raise Status(Status[status]).raise_exception()

    def _parse_addr(self, data):
        res = []

        for addr in data:
            res.append(
                AddressComponent(addr['long_name'], addr['short_name'], addr[
                    'types']))

        return res

    def _parse_geopair(self, data):
        return GeoPair(data['northeast'], data['southwest'])

    def _parse_location(self, data):
        return Location(data)

    def serialize(self):
        '''Inverse the data back to its initial JSON format.
        
        Serialize is an inverse function on object, it maps object back
        to initial data format. That makes Gobject instance behave like
        a bijecive function.
        '''
        return self.__dict__()

    def __repr__(self):
        # Get representation of each component.
        components = []
        for component in self.address_components:
            components.append(component.__repr__())

        addr = '<<address_components: {}>, '.format(components)
        fmt = '<formatted_address: {0}>, '.format(self.formatted_address)
        geo = '<geometry: <bounds: {0}>, '.format(self.bounds)
        loc = '<location:{0}>, '.format(self.location)
        loct = '<location_type: {0}>, '.format(self.location_type)
        view = '<viewport: {0}>>, '.format(self.viewport)
        pid = '<place_id: {0}>, '.format(self.place_id)
        types = '<types: {0}>>'.format(self.types)

        return addr + fmt + geo + loc + loct + view + pid + types

    def __dict__(self):
        components = []
        for component in self.address_components:
            components.append(component.__dict__())

        return {
            'results': [{
                'address_components': components,
                'formatted_address': self.formatted_address,
                'geometry': {
                    'bounds': self.bounds.__dict__(),
                    'location': self.location.__dict__(),
                    'location_type': self.location_type,
                    'viewport': self.viewport.__dict__()
                },
                'place_id': self.place_id,
                'types': self.types
            }],
            "status": Status(1).name
        }

    def __eq__(self, other):
        addr = (self.address_components == other.address_components)
        fmt_addr = (self.formatted_address == other.formatted_address)
        bounds = (self.bounds == other.bounds)
        loc = (self.location == other.location)
        view = (self.viewport == other.viewport)
        loc_t = (self.location_type == other.location_type)
        p_id = (self.place_id == other.place_id)
        types = (self.types == other.types)

        res = (addr and fmt_addr and bounds and loc and view and loc_t and
               p_id and types)

        if res:
            return True
        else:
            return False
