from coordinates import Coordinate
from numpy.random import randn
from uuid import uuid1
from pymongo import MongoClient
import pymongo
from datetime import datetime, timedelta
import time
from maps_api_key import key
import googlemaps

gmaps = googlemaps.Client(key=key)

def get_travel_information(origin, destination):
    directions_result = gmaps.directions(origin, destination, mode="driving", departure_time=datetime.now())
    distance_in_meters = directions_result[0]['legs'][0]['distance']['value']
    duration_in_seconds = directions_result[0]['legs'][0]['duration']['value']
    return distance_in_meters, duration_in_seconds

class CarSim:

    def __init__(self, home_coord, work_coord, work_start, work_end, weekend_coord, traveled_distance=0):
        self.home_coord = home_coord
        self.work_coord = work_coord
        self.work_start = work_start
        self.work_end = work_end
        self.weekend_coord = weekend_coord
        self.traveled_distance = traveled_distance
        self.last_updated = datetime.now()
        self.id = uuid1()
        self.location = self.set_current_location()

    def run(self):
        while True:
            next_event = self.get_next_event()
            self.sleep_till_next_event(next_event)
            distance, start, finish = self.travel(next_event)

            update = {
                'duration' : {
                    'start' : start,
                    'stop' : finish
                },
                'distance' : distance,
                'car_id' : self.id
            }

            self.save(update)
            self.last_updated = datetime.now()

    def travel(self, next_event):
        distance, duration = get_travel_information(self.location, next_event['location'])
        start = datetime.now()
        self.sleep_till_end_of_trip(duration)
        finish = datetime.now()
        self.location = next_event['location']
        self.traveled_distance += distance
        return distance, start, finish

    def save(self, update):
        pass

    def set_current_location(self, location=None):
        pass

    def get_next_event(self):
        pass

    def sleep_till_next_event(self, next_event):
        pass

    def sleep_till_end_of_trip(self, duration):
        time.sleep(duration)
