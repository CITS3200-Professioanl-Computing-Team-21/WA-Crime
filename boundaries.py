import os
import numpy as np
import pandas as pd
import json
import haversine as hs
from fuzzywuzzy import process
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from os.path import join
import geopandas as gpd
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
        zones[row[0].lower()] = {
            'station': row[1].lower(), 
            'district': row[2].lower(), 
            'region': row[3].lower()}

    return (landgate_data, landgate_locations, crime_locations, zones_data, zones)

def check_naming(zones_data, landgate_locations, crime_locations):
    zones_suburbs = np.char.lower(zones_data['SUB_TXT'].unique().astype('str'))
    for location in crime_locations:
        missing1 = [location for location in crime_locations if location not in zones_suburbs]
        missing2 = [location for location in crime_locations if location not in landgate_locations]
    changes = []
    if not missing1:
        if missing2: 
            for location in missing2:
                highest = process.extractOne(location, landgate_locations)
                landgate_location, score = highest[0], highest[1]
                if landgate_location not in crime_locations and score > 85:
                    changes.append((location, landgate_location))
                    missing2.remove(location)
    return (missing2, changes)

def missing_locations(zones, zones_data, missing2):
    zones_stations = np.char.lower(zones_data['STATION'].unique().astype('str'))
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
        if getLoc:
            missing_point = (getLoc.latitude, getLoc.longitude)
            station_coordinate = station_coordinates[zones[location]['station']]
            if hs.haversine(missing_point, station_coordinate) <= 200:
                missing_landgate[location] = {
                    'coordinates': missing_point,
                    'station': zones[location]['station'],
                    'district': zones[location]['district'],
                    'region': zones[location]['region']
                }
            else: print('>200', location)
        else : print('not found', location)

    return (missing_landgate)

def assign_missing_boundaries(missing_landgate, landgate_data, changes, crime_locations):
    for location in missing_landgate:
        point = Point(missing_landgate[location]['coordinates'][1], missing_landgate[location]['coordinates'][0])
        for i in landgate_data['features']:
            polygon = shape(i['geometry'])
            landgate_location = i['properties']['name'].lower()
            if polygon.contains(point) and landgate_location not in crime_locations:
                changes.append((location, landgate_location))
    return (changes)

def zoning_boundaries(changes, landgate_data, zones, crime_locations, landgate_locations):
    final_data = {'suburbs': {}, 'stations': {}, 'districts': {}, 'regions': {}}
    missing = [location for location in crime_locations if location not in landgate_locations]
    for i in landgate_data['features']:
        name = i['properties']['name'].lower()
        if name in crime_locations and name not in missing:
            polygon = shape(i['geometry'])
            final_data['suburbs'][name] = zones[name]
            final_data['suburbs'][name]['coordinates'] = polygon
    
    polygons = []
    for i in final_data['suburbs']:
        polygons.append(final_data['suburbs'][i]['coordinates'])
    boundary = gpd.GeoSeries(unary_union(polygons).simplify(tolerance=0.001))

    return(final_data, boundary)
    
    # m = folium.Map(location=[-32, 116],
    #        zoom_start=12,
    #        tiles='https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    #        attr='Trial Heatmap')
    # geo_j = boundary.to_json()
    # folium.GeoJson(geo_j).add_to(m)
    # m.save('test.html')

def main():
    for file in files:
        if check_file(file) == None:
            return None
    landgate_data, landgate_locations, crime_locations, zones_data, zones = data_loading(DATA, LANDGATE, ZONES)
    missing2, changes = check_naming(zones_data, landgate_locations, crime_locations)
    missing_landgate = missing_locations(zones, zones_data, missing2)
    changes = assign_missing_boundaries(missing_landgate, landgate_data, changes, crime_locations)
    final_data = zoning_boundaries(changes, landgate_data, zones, crime_locations, landgate_locations)
    print(final_data)

if __name__ == '__main__':
    main()


