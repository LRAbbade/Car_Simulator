from coordinates import Coordinate
from numpy.random import randn
import random
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

def save_to_mongo(car_number, document):
    print('$ Car number:', car_number, 'saving trip in mongo')
    r = db.raw_sim_data.insert_one(raw_data)
    if not r.acknowledged:
        raise Exception('Error in MongoDB at car ' + str(car_number))

def get_travel_information(origin, destination):
    directions_result = gmaps.directions(origin, destination, mode="driving", departure_time=datetime.now())
    distance_in_meters = directions_result[0]['legs'][0]['distance']['value']
    duration_in_seconds = directions_result[0]['legs'][0]['duration']['value']
    steps = directions_result[0]['legs'][0]['steps']
    steps_filtered = [{'start_location':Coordinate(**i['start_location']),
                       'end_location':Coordinate(**i['end_location']),
                       'duration':i['duration']['value']} for i in steps]
    return steps_filtered, distance_in_meters, duration_in_seconds

class CarSim:

    def __init__(self, home_coord, work_coord, work_start, work_end, weekend_coord, traveled_distance=0, car_number=0):
        if not isinstance(home_coord, Coordinate) or not isinstance(work_coord, Coordinate) or not isinstance(weekend_coord, Coordinate):
            raise Exception('Car locations should be a Coordinate object')
        if not isinstance(work_start, int) or not isinstance(work_end, int) or not 2 <= work_start < 22 or not 2 <= work_end < 22:      # 2 and 22 will make it easier to calculate the next event
            raise Exception('work hours should be an int between 0 and 22')
        if work_start >= work_end:
            raise Exception('work_start should be before work_end')

        self.home_coord = home_coord
        self.work_coord = work_coord
        self.work_start = work_start
        self.work_end = work_end
        self.weekend_coord = weekend_coord
        self.traveled_distance = traveled_distance
        self.car_number = car_number
        self.last_updated = datetime.now()
        self.id = uuid1()
        self.location = home_coord
        print('Car', self.car_number, 'started:')
        self.__repr__()

    def run(self):
        while True:
            print('$ Car number:', self.car_number, 'current location:', self.get_car_location())
            print('$ Car number:', self.car_number, 'odometer as of', datetime.now(), ':', self.get_odometer(), 'meters')
            next_event = self.get_next_event()
            self.sleep_till_next_event(next_event)
            trip = self.travel(next_event)

            geo_json_trip = [{'location':i['location'].get_geo_json(),
                              'time':i['time']} for i in trip]

            raw_data = {
                'car_id' : self.id,
                'insertion_time' : datetime.now(),
                'trip' : geo_json_trip
            }

            self.save_in_db(raw_data)
            self.last_updated = datetime.now()

    def travel(self, next_event):
        print('$ Car number:', self.car_number, 'running next trip')
        trip, distance, duration = get_travel_information(self.location.get_tuple(), next_event['location'].get_tuple())
        self.sleep_till_end_of_trip(duration)
        self.location = next_event['location']
        self.traveled_distance += distance
        return self.filter_trip(trip)

    def filter_trip(self, trip):
        current_time = datetime.now()
        r = [{'location':trip[0]['start_location'],
              'time':current_time}]

        for i in trip:
            current_time += timedelta(seconds=i['duration'])
            r.append({
                'location':i['end_location'],
                'time':current_time
            })

        return r

    def get_odometer(self):
        return self.traveled_distance

    def save_in_db(self, raw_data):
        save_to_mongo(self.car_number, raw_data)

    def get_next_event(self):
        print('$ Car number:', self.car_number, 'getting next event')
        today = datetime.now()
        day_of_week = today.weekday()
        current_hour = today.hour
        current_location = self.get_car_location()

        if current_location == 'home':
            if day_of_week == 4 and self.work_end <= current_hour:  # friday night
                print('$ Car number:', self.car_number, ' * currently friday night')
                event_time = datetime(today.year, today.month, today.day, random.randint(current_hour + 1, 24), 0)
                event_location = self.weekend_coord
            else:
                print('$ Car number:', self.car_number, ' * currently at home')
                if current_hour >= self.work_start:
                    print('$ Car number:', self.car_number, 'going to sleep')
                    today += timedelta(hours=(25 - current_hour))

                event_time = datetime(today.year, today.month, today.day, self.work_start, 0)
                event_location = self.work_coord
        elif current_location == 'work':
            print('$ Car number:', self.car_number, ' * currently at work')
            event_time = datetime(today.year, today.month, today.day, self.work_end, 0)
            event_location = self.home_coord
        elif current_location == 'weekend':
            print('$ Car number:', self.car_number, ' * currently at weekend')
            day_diff = 6 - day_of_week
            event_time = today + timedelta(days=day_diff)
            event_time = datetime(event_time.year, event_time.month, event_time.day, random.randint(12, 24), 0)     # get a random hour between 12 and 24 in the next sunday, which is going to be the trip back start time
            event_location = self.home_coord
        else:       # unknown location (shouldnt happen)
            raise Exception('Unknown car location ' + str(self.car_number))

        print('$ Car number:', self.car_number, ' * current time:', datetime.now())
        print('$ Car number:', self.car_number, ' * getting time variation')
        time_var = -timedelta(days=10)              # just to guarantee
        tries = 0
        while event_time + time_var <= datetime.now():
            print('$ Car number:', self.car_number, ', possible event time:', event_time + time_var)
            time_var = timedelta(minutes=randn()*10)        # create a normally distributed time variance to make times seem more natural
            tries += 1
            if tries > 1000:
                raise Exception('Couldnt get variation in car ' + str(self.car_number))

        event = {
            'location' : event_location,
            'time' : event_time + time_var
        }

        self.print_next_event(event)
        return event

    def print_next_event(self, event):
        print('$ Car number:', self.car_number, 'Next event:',
              '\nlocation:', self.check_location_definition(event['location']),
              '\ntime:', event['time'], '\n')

    def sleep_till_next_event(self, next_event):
        time_to_sleep = int((next_event['time'] - datetime.now()).total_seconds())
        print('$ Car number:', self.car_number, 'sleeping', time_to_sleep, 'seconds until next event\n')
        time.sleep(time_to_sleep)

    def sleep_till_end_of_trip(self, duration):
        time.sleep(duration)

    def check_location_definition(self, coord):
        if coord == self.home_coord:
            return 'home'
        elif coord == self.work_coord:
            return 'work'
        elif coord == self.weekend_coord:
            return 'weekend'
        else:
            return 'coordinate unknown: ' + str(coord)

    def get_car_location(self):
        r = self.check_location_definition(self.location)
        if r.startswith('coordinate unknown'):
            raise Exception('Vehicle location unknown. Car number: ' + str(self.car_number))

        return r

    def __repr__(self):
        print('$ Car number:', self.car_number,
              '\nCar simulator instance:', self.id,
              '\nHome:', self.home_coord,
              '\nWork:', self.work_coord,
              '\nWeekend:', self.weekend_coord,
              '\nWork hours:', self.work_start, self.work_end,
              '\nOdometer:', self.get_odometer(), '\n')
