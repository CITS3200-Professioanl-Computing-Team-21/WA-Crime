import pandas as pd
import json
import requests

DATA = '/Users/adityagupta/Desktop/UWA/Data Science/CITS3200 - Professional Computing/WA Police Heatmap/data.csv'

API_KEY = 'AIzaSyB84cidDJ-8rusBSb_VstKUOhdgtY1y0Js'
BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json?'

crime_data = pd.read_csv(DATA)
locations = crime_data['Suburb'].unique()

coordinates = []
for location in locations:
    address = location + ', WA, Australia'
    params = {
    'key': API_KEY,
    'address': address,
    }
    response = requests.get(BASE_URL, params=params)
    api_data = response.json()
    coords = api_data['results'][0]['geometry']
    coordinates.append(coords)
i = 0
for dict in coordinates:
    dict['name'] = locations[i]
    i +=1
jsonString = json.dumps(coordinates)
jsonFile = open("locations.json", "w")
jsonFile.write(jsonString)
jsonFile.close()

latlong = {}
for location in locations:
    for coords in coordinates:
        if coords['name'] == location: 
            latlong[location] = [coords['location']['lat'], coords['location']['lng']]
jsonString = json.dumps(latlong)
jsonFile = open("coordinates.json", "w")
jsonFile.write(jsonString)
jsonFile.close()

