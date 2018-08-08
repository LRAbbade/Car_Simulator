from multiprocessing import Pool
from CarSimulator import CarSim
from coordinates import Coordinate
from datetime import datetime
from pprint import pprint

cars = [
    CarSim(home_coord=Coordinate(-22.255119, -45.709408),
           work_coord=Coordinate(-22.257200, -45.696122),
           work_start=6,
           work_end=16,
           weekend_coord=Coordinate(-21.677732, -45.920903),
           car_number=1),
    CarSim(home_coord=Coordinate(-23.564407, -46.671967),
           work_coord=Coordinate(-23.538597, -46.657996),
           work_start=7,
           work_end=17,
           weekend_coord=Coordinate(-23.964221, -46.326848),
           car_number=2),
    CarSim(home_coord=Coordinate(-23.200130, -45.894011),
           work_coord=Coordinate(-23.196123, -45.906720),
           work_start=8,
           work_end=18,
           weekend_coord=Coordinate(-22.921429, -47.073315),
           car_number=3),
    CarSim(home_coord=Coordinate(-22.911632, -47.043178),
           work_coord=Coordinate(-22.907581, -47.097748),
           work_start=9,
           work_end=19,
           weekend_coord=Coordinate(-22.014015, -47.889684),
           car_number=4),
    CarSim(home_coord=Coordinate(-19.755719, -47.937090),
           work_coord=Coordinate(-19.755935, -47.950140),
           work_start=10,
           work_end=20,
           weekend_coord=Coordinate(-19.942181, -43.965867),
           car_number=5)
]

for car in cars:
    car.location = car.work_coord        # not necessary

def run(obj):
    obj.run()

print('$ Starting pool')
with Pool(len(cars)) as pool:
    pool.map(run, cars)
