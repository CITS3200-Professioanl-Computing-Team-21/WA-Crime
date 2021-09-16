import os
import numpy as np
import pandas as pd
import json
import haversine as hs
from fuzzywuzzy import process
from shapely.geometry import Point, shape
from os.path import join
from geopy.geocoders import Nominatim

DATA = 'Locality_Data_Filtered (from Quart Website Rep Mar213-2.csv'
LANDGATE = 'Localities_LGATE_234_WA_GDA2020_Public.geojson'
ZONES = 'Suburb Locality.csv'
files = [DATA, LANDGATE, ZONES]

def check_file(file): #to check if file exists
    if not os.path.isfile(file): 
        return None
    else:
        return True

def data_loading(crime, landgate, zones):
    
    with open(LANDGATE) as f:
        landgate_data = json.load(f)
        landgate_locations = [i['properties']['name'].lower() for i in landgate_data['features']]

    crime_data = pd.read_csv(crime)
    crime_locations = np.char.lower(crime_data['Suburb'].unique().astype('str'))
    
    zones_data = pd.read_csv(zones)
    # zones_suburbs = np.char.lower(zones_data['SUB_TXT'].unique().astype('str'))
    zones = {}
    for index, row in zones_data.iterrows():
        zones[row[0]]['station'] = row[1].lower()
        zones[row[0]]['district'] = row[2].lower()
        zones[row[0]]['region'] = row[3].lower()

    return (landgate_data, landgate_locations, crime_locations, zones_data, zones)

def missing_locations(landgate_locations, crime_locations, zones, zones_data):
    zones_suburbs = np.char.lower(zones_data['SUB_TXT'].unique().astype('str'))
    zones_stations = np.char.lower(zones_data['STATION'].unique().astype('str'))
    for location in crime_locations:
        missing1 = [location for location in crime_locations if location not in zones_suburbs]
        missing2 = [location for location in crime_locations if location not in landgate_locations]
    if not missing1:
        if missing2:
            station_coordinates = {}
            for station in zones_stations:
                # calling the Nominatim tool
                loc = Nominatim(user_agent="GetLoc") 
                # entering the location name
                getLoc = loc.geocode(station+', WA, Australia')
                station_coordinates[station] = (getLoc.latitude, getLoc.longitude)
            missing_landgate = {}
            for location in missing2:
                # calling the Nominatim tool
                loc = Nominatim(user_agent="GetLoc") 
                # entering the location name
                getLoc = loc.geocode(location+', WA, Australia')
                missing_point = (getLoc.latitude, getLoc.longitude)
                station_coordinate = station_coordinates[zones[location]['station']]
                if hs.haversine(missing_point, station_coordinate) <= 200:
                    missing_landgate[location]['coordinates'] = missing_point
                    missing_landgate[location]['station'] = zones[location]['station']
                    missing_landgate[location]['district'] = zones[location]['district']
                    missing_landgate[location]['region'] = zones[location]['region']
                else: print(location)
        missing3 = [i for i in list(missing_landgate.keys())]

    return (missing3, missing_landgate)

def assign_missing_boundaries(missing3, missing_landgate, landgate_locations, crime_locations, landgate_data):
    changes = []
    for location in missing3:
        highest = process.extractOne(location, landgate_locations)
        landgate_location, score = highest[0], highest[1]
        if landgate_location not in crime_locations and score > 85:
            changes.append((location, landgate_location))
            missing3.remove(location)

    for location in missing_landgate:
        point = Point(missing_landgate[location]['coordinates'][0], missing_landgate[location]['coordinates'][1])
        for i in landgate_data['features']:
            polygon = shape(i['geometry'])
            landgate_location = i['properties']['name'].lower()
            if polygon.contains(point):
                changes.append((location, landgate_location))
    return (changes)

def zoning_boundaries(changes):



# from shapely.ops import cascaded_union
# polygons = [poly1[0], poly1[1], poly2[0], poly2[1]]
# boundary = gpd.GeoSeries(cascaded_union(polygons))
# boundary.plot(color = 'red')
# plt.show()

def main():
    for file in files:
        if check_file(file) == None:
            return None
    landgate_data, landgate_locations, crime_locations, zones_data, zones = data_loading(DATA, LANDGATE, ZONES)
    missing3, missing_landgate = missing_locations(landgate_locations, crime_locations, zones, zones_data)
    changes = assign_missing_boundaries(missing3, missing_landgate, landgate_locations, crime_locations, landgate_data)

if __name__ == '__main__':
    main()


