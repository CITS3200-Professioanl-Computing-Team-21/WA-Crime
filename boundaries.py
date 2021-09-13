import numpy as np
import pandas as pd
import json
from fuzzywuzzy import process
from shapely.geometry import Point, shape
from os.path import join

DATA = 'crime.csv'
COORDINATES = 'coordinates.json'
LANDGATE = 'Localities_LGATE_234_WA_GDA2020_Public.geojson'
ZONES = 'zones.csv'

crime_data = pd.read_csv(DATA)
zones_data = pd.read_csv(ZONES)
with open(COORDINATES) as f:
    coordinates_data = json.load(f)
with open(LANDGATE) as f:
    landgate_data = json.load(f)

crime_locations = np.char.lower(crime_data['Suburb'].unique().astype('str'))
zones_suburbs = np.char.lower(zones_data['SUB_TXT'].unique().astype('str'))

# for location in crime_locations:
#     if location not in zones_suburbs:
#         print(location)

landgate_locations = [i['properties']['name'].lower() for i in landgate_data['features']]

missing = []
for i in crime_locations:
    if i not in landgate_locations:
        missing.append(i)

for i in missing:
    highest = process.extractOne(i,landgate_locations)
    name = highest[0]
    if name not in crime_locations:
        print(i, highest)

final_data = []
for place in missing:
  point = Point(coordinates_data[place][1], coordinates_data[place][0])
  for i in landgate_data['features']:
    polygon = shape(i['geometry'])
    if polygon.contains(point):
      final_data.append([place.lower(), i['properties']['name'].lower()])

for i in final_data:
    if i[1] in crime_locations:
        print(i)


# importing geopy library
from geopy.geocoders import Nominatim
  
# calling the Nominatim tool
loc = Nominatim(user_agent="GetLoc")
  
# entering the location name
getLoc = loc.geocode("Wannoo, Shark Bay, WA, Australia")
  
# printing address
print(getLoc.address)
  
# printing latitude and longitude
print("Latitude = ", getLoc.latitude, "\n")
print("Longitude = ", getLoc.longitude)







