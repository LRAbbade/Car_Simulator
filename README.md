# Car Simulator
A Python class to simulate the average movements of a car in a day.

## Instructions:
To run, you will need a running MongoDB and a Google Maps API key.
Create a file called `db_connector.py` with the function `get_mongo_client`, where you are gonna return a `MongoClient` to connect to your database.

As for the Google Maps Key, create a file `maps_api_key.py` with a variable `key`, which is going to be a `str` with your API Key.

The `main.py` file has an example with 5 threads running parallel instances of cars.

## Requirements:

| Library		| Version   |
|--------------:|:---------:|
| geopy 		| 1.16.0	|
| googlemaps 	| 3.0.2	    |
| numpy 	    | 1.13.3    |
| pymongo 	    | 3.6.0	    |
