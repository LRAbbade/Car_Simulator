import numpy as np

class Coordinate:

    def __init__(self, lat=0, long=0):
        self.lat = lat
        self.long = long

    def get_tuple(self):
        return (self.lat, self.long)

    def __getitem__(self, key):
        if key is 'lat' or key is 0:
            return self.lat
        elif key is 'long' or key is 1:
            return self.long
        else:
            raise Exception('Invalid key for coordinate')

    def __setitem__(self, key, value):
        if not isinstance(value, float):       # this can probably be better
            raise Exception('Invalid value for coordinate')

        if key is 'lat' or key is 0:
            self.lat = value
        elif key is 'long' or key is 1:
            self.long = value
        else:
            raise Exception('Invalid key for coordinate')

    def __str__(self):
        return '(' + str(self.lat) + ', ' + str(self.long) + ')'

    def __repr__(self):
        return 'Coordinate object: ' + self.__str__()
