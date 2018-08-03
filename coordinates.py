from geopy.distance import geodesic

class Coordinate:

    @staticmethod
    def distance(c1, c2):
        if isinstance(c1, Coordinate):
            c1 = c1.get_tuple()
        if isinstance(c2, Coordinate):
            c2 = c2.get_tuple()

        if not isinstance(c1, tuple) or not isinstance(c2, tuple):
            raise Exception('Both coordinates should be either a tuple or a Coordinate Object')

        return geodesic(c1, c2).meters

    def __init__(self, lat=0, lng=0):
        self.lat = lat
        self.lng = lng

    def get_tuple(self):
        return (self.lat, self.lng)

    def get_geo_json(self):
        return {"type": "Point", "coordinates": [self.lng, self.lat]}

    def __getitem__(self, key):
        if key is 'lat' or key is 0:
            return self.lat
        elif key is 'lng' or key is 1:
            return self.lng
        else:
            raise Exception('Invalid key for coordinate')

    def __setitem__(self, key, value):
        if not isinstance(value, float):       # this can probably be better
            raise Exception('Invalid value for coordinate')

        if key is 'lat' or key is 0:
            self.lat = value
        elif key is 'lng' or key is 1:
            self.lng = value
        else:
            raise Exception('Invalid key for coordinate')

    def __str__(self):
        return '(' + str(self.lat) + ', ' + str(self.lng) + ')'

    def __repr__(self):
        return 'Coordinate object: ' + self.__str__()
