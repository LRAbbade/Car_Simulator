from coordinates import Coordinate
from numpy.random import randn
from uuid import uuid1
from db_connector import get_mongo_client
from pymongo import MongoClient
import pymongo
from datetime import datetime, timedelta
import time
from pprint import pprint
from maps_api_key import key
import googlemaps

gmaps = googlemaps.Client(key=key)
mongo_client = get_mongo_client()
db = mongo_client.carChain

def get_travel_information(origin, destination):
    directions_result = gmaps.directions(origin, destination, mode="driving", departure_time=datetime.now())
    distance_in_meters = directions_result[0]['legs'][0]['distance']['value']
    # duration_in_seconds = directions_result[0]['legs'][0]['duration']['value']
    steps = directions_result[0]['legs'][0]['steps']
    steps_filtered = [{'start_location':Coordinate(**i['start_location']),
                       'end_location':Coordinate(**i['end_location'])} for i in steps]
    return steps_filtered, distance_in_meters

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
        self.location = home_coord

    def run(self):
        while True:
            next_event = self.get_next_event()
            self.sleep_till_next_event(next_event)
            trip = self.travel(next_event)

            geo_json_trip = [{'start_location':i['start_location'].get_geo_json(),
                              'end_location':i['end_location'].get_geo_json()} for i in trip]

            raw_data = {
                'car_id' : self.id,
                'insertion_time' : datetime.now(),
                'trip' : geo_json_trip
            }

            self.save_in_db(raw_data)
            self.last_updated = datetime.now()
            break

    def travel(self, next_event):
        trip, distance = get_travel_information(self.location.get_tuple(), next_event['location'].get_tuple())
        self.location = next_event['location']
        self.traveled_distance += distance
        return trip

    def get_odometer(self):
        return self.traveled_distance

    def save_in_db(self, raw_data):
        r = db.raw_sim_data.insert_one(raw_data)
        if not r.acknowledged:
            raise Exception('Error in MongoDB')

    def get_next_event(self):
        time_var = timedelta(minutes=randn()*10)

    def sleep_till_next_event(self, next_event):
        pass

    def sleep_till_end_of_trip(self, duration):
        time.sleep(duration)
