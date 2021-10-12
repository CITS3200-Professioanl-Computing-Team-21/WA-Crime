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
import map as mp
import folium
from geopandas import GeoDataFrame

DATA = 'crime.csv'
LANDGATE = 'Localities_LGATE_234_WA_GDA2020_Public.geojson'
ZONES = 'Suburb Locality.csv'
files = [DATA, LANDGATE, ZONES]

# function - to check if required files exist
def check_file(file):
    if not os.path.isfile(file): 
        return None
    else:
        return True

# function - to extract data from datafiles and intiate cleaning
def data_loading(crime, landgate, zones):
    with open(LANDGATE) as f:
        landgate_data = json.load(f)
        landgate_locations = [i['properties']['name'].lower() for i in landgate_data['features']]

    crime_data = pd.read_csv(DATA)
    # selects all unique string values from first column and converts to lowercase, output = array
    crime_locations = np.char.lower(crime_data.iloc[:, 0].unique().astype('str'))
    
    # reads dataframe, converts all values to string and lowercase
    zones_data = pd.read_csv(zones).apply(lambda x: x.astype(str).str.lower())
    zones_data.columns = ['suburbs', 'stations', 'districts', 'regions']
    # converts dataframe into a dictionary where each key, value pair = 'column name': [column values as a list]
    zones = zones_data.to_dict(orient="list")
    for i in zones:
        zones[i] = np.unique(np.array(zones[i]))
    return (landgate_data, landgate_locations, crime_locations, zones_data, zones)

def check_naming(landgate_locations, crime_locations, zones):
    for location in crime_locations:
        missing1 = [location for location in crime_locations if location not in zones['suburbs']]
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

def missing_locations(zones_data, zones, missing2):
    station_coordinates = {}
    for station in zones['stations']:
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
            station_name = zones_data.loc[zones_data['suburbs'] == location, 'stations'].item()
            station_coordinate = station_coordinates[station_name]
            if hs.haversine(missing_point, station_coordinate) <= 200:
                missing_landgate[location] = missing_point
            else: print('>200', location)
        else : print('not found', location)
    return (missing_landgate)

def assign_missing_boundaries(missing_landgate, landgate_data, changes, crime_locations):
    for location in missing_landgate:
        point = Point(missing_landgate[location][1], missing_landgate[location][0])
        for i in landgate_data['features']:
            polygon = shape(i['geometry'])
            landgate_location = i['properties']['name'].lower()
            if polygon.contains(point) and landgate_location not in crime_locations:
                changes.append((location, landgate_location))
    return (changes)

def zoning_boundaries(changes, landgate_data, zones, crime_locations, landgate_locations, zones_data):
    final_data = {'suburbs': {}, 'stations': {}, 'districts': {}, 'regions': {}}
    for zone_type in zones:
        if zone_type != 'suburbs':
            for location in zones[zone_type]:
                boundary_locations = list(zones_data.loc[zones_data[zone_type] == location, 'suburbs'])
                boundary_locations_landgate = []
                for i in boundary_locations:
                    if i in landgate_locations:
                        boundary_locations_landgate.append(i)
                final_data[zone_type][location] = boundary_locations_landgate
        
    for location in landgate_data['features']:
        name = location['properties']['name'].lower()
        if name in zones['suburbs']:
            final_data['suburbs'][name] = location['geometry']
                    
    for zone_type in final_data:
        if zone_type != 'suburbs':
            for place in final_data[zone_type]:
                polygons = []
                for location in final_data[zone_type][place]:
                    polygons.append(shape(final_data['suburbs'][location]))
                boundary = gpd.GeoSeries(unary_union(polygons).simplify(tolerance=0.001))
                final_data[zone_type][place] = boundary.to_json()

    return(final_data)

def choropleth(query):
    results = mp.main(query)
    results['name'] = results['name'].str.upper()
    results['log'] = np.log(results['sum']+1)

    data = gpd.read_file(LANDGATE)
    data['name'] = data['name'].str.upper()
    for_plotting = results.merge(data, left_on = 'name', right_on = 'name')
    merged = GeoDataFrame(for_plotting)
    geo_j = merged.to_json()

    #Creating a map object for choropleth map
    #Starting location coordinates [lat, long] set to Perth
    choropleth = folium.Map(
        location=[-32, 116],
        tiles='https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        zoom_start=12,
        attr='Trial Heatmap')

    #Creating choropleth map object with key on suburb name
    folium.Choropleth(
        geo_data = geo_j, #Assign geo_data to your geojson file
        name = "WA Crime Heat Map",
        data = results, #Assign dataset of interest
        columns = ['name', 'log'], #Assign columns in the dataset for plotting
        key_on = 'feature.properties.name', #Assign the key that geojson uses to connect with dataset
        fill_color = 'YlOrRd',
        fill_opacity = 0.9,
        line_opacity = 0.5,
        bins = 9,
        legend_name = 'legend').add_to(choropleth)
    
    #Creating style_function
    style_function = lambda x: {
                    'fillColor': '#ffffff', 
                    'color':'#000000', 
                    'fillOpacity': 0.1, 
                    'weight': 0.1}

    #Creating highlight_function
    highlight_function = lambda x: {
                    'fillColor': '#000000', 
                    'color':'#000000', 
                    'fillOpacity': 0.50, 
                    'weight': 0.1}

    #Creating popup tooltip object
    NIL = folium.features.GeoJson(
        geo_j,
        style_function=style_function, 
        control=False,
        highlight_function=highlight_function, 
        tooltip=folium.features.GeoJsonTooltip(
            fields=['name'],
            aliases=['name'],
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")))

    #Adding tooltip object to the map
    choropleth.add_child(NIL)
    choropleth.keep_in_front(NIL)
    folium.LayerControl().add_to(choropleth)

    choropleth.save('trial.html')
    
def main():
    for file in files:
        if check_file(file) == None:
            return None
    # landgate_data, landgate_locations, crime_locations, zones_data, zones = data_loading(DATA, LANDGATE, ZONES)
    # missing2, changes = check_naming(landgate_locations, crime_locations, zones)
    # missing_landgate = missing_locations(zones_data, zones, missing2)
    # changes = assign_missing_boundaries(missing_landgate, landgate_data, changes, crime_locations)
    # final_data = zoning_boundaries(changes, landgate_data, zones, crime_locations, landgate_locations, zones_data)
    choropleth(query)
    # return final_data

if __name__ == '__main__':
    main()