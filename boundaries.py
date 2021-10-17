import os
import json
import folium
import numpy as np
import pandas as pd
import geopandas as gpd
import haversine as hs
import filter as filter
from fuzzywuzzy import process
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from geopy.geocoders import Nominatim
from geojson import Point, Feature, FeatureCollection, dump

# constant variables conatining paths to data files
CRIME = 'crime.csv'
LANDGATE = 'Localities_LGATE_234_WA_GDA2020_Public.geojson'
ZONES = 'Suburb Locality.csv'
FILES = [CRIME, LANDGATE, ZONES]

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

    crime_data = pd.read_csv(CRIME)
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
                       
    features_stations = []
    features_districts = []
    features_regions = []
    stations_dict = {}
    districts_dict = {}
    regions_dict = {}
    for zone_type in final_data:
        if zone_type != 'suburbs':
            for place in final_data[zone_type]:
                polygons = []
                for location in final_data[zone_type][place]:
                    polygons.append(shape(final_data['suburbs'][location]))
    #             boundary = gpd.GeoSeries(unary_union(polygons).simplify(tolerance=0.001))
                polygon = unary_union(polygons).simplify(tolerance=0.001)
                try:
                    x = polygon.centroid.x
                    y = polygon.centroid.y
                except IndexError:
                    x = ''
                    y = ''
    #             polygon = MultiPolygon(boundary)
                if zone_type == 'stations':
                    features_stations.append(Feature(geometry=polygon, properties={'zone_type': zone_type, 'name': place}))
                    stations_dict[place] = [y, x]
                if zone_type == 'districts':
                    features_districts.append(Feature(geometry=polygon, properties={'zone_type': zone_type, 'name': place}))
                    districts_dict[place] = [y, x]
                if zone_type == 'regions':
                    features_regions.append(Feature(geometry=polygon, properties={'zone_type': zone_type, 'name': place}))
                    regions_dict[place] = [y, x]
    #             final_data[zone_type][place] = boundary.to_json()

    landgate_gpd = gpd.read_file(LANDGATE)
    selected_features = landgate_gpd[['name', 'postcode', 'land_area','geometry']]
    selected_features.to_file('/Users/adityagupta/Documents/GitHub/WA-Crime/zones/suburbs.geojson', driver="GeoJSON")

    feature_collection_stations = FeatureCollection(features_stations)
    with open('stations.geojson', 'w') as f:
        dump(feature_collection_stations, f)
    feature_collection_districts = FeatureCollection(features_districts)
    with open('districts.geojson', 'w') as f:
        dump(feature_collection_districts, f)
    feature_collection_regions = FeatureCollection(features_regions)
    with open('regions.geojson', 'w') as f:
        dump(feature_collection_regions, f)
    
    jsonString = json.dumps(stations_dict)
    jsonFile = open("station_centroids.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()

    jsonString = json.dumps(districts_dict)
    jsonFile = open("district_centroids.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()

    jsonString = json.dumps(regions_dict)
    jsonFile = open("region_centroids.json", "w")
    jsonFile.write(jsonString)
    jsonFile.close()

    return(final_data)

def choropleth(query):
    #results, stat, png = mp.main(query)
    path = os.getcwd()
    COORDINATES = path + "/centroids/coordinates.json"
    STATIONS = path + "/centroids/station_centroids.json"
    DISTRICTS = path + "/centroids/district_centroids.json"
    REGIONS = path + "/centroids/region_centroids.json"

    results, anomalies, plot = filter.filter(query[0], query[1], query[2], query[3], query[4])
    results['name'] = results['name'].str.upper()
    results['log'] = np.log(results['sum']+1)

    if (query[1] == 'suburb') or (query[1] == 'station' and query[0].lower() != 'all'):
        data = gpd.read_file(path + '/zones/suburbs.geojson')
        starting_zoom = 12
        fields = ['name', 'postcode', 'land_area','sum']
        aliases = ['Name', 'Postcode', 'Land Area', query[-1].upper()+' Crime Frequency']
    if (query[1] == 'district' and query[0].lower() != 'all') or (query[1] == 'station' and query[0].lower() == 'all'):
        data = gpd.read_file(path + '/zones/stations.geojson')
        starting_zoom = 9
        fields = ['name', 'zone_type', 'sum']
        aliases = ['Name', 'Zone Type', query[-1].upper()+' Crime Frequency']
    if (query[1] == 'region' and query[0].lower() != 'all') or (query[1] == 'district' and query[0].lower() == 'all'):
        data = gpd.read_file(path + '/zones/districts.geojson')
        starting_zoom = 5
        fields = ['name', 'zone_type', 'sum']
        aliases = ['Name', 'Zone Type', query[-1].upper()+' Crime Frequency']
    if (query[1] == 'region' and query[0].lower() == 'all'):
        data = gpd.read_file(path + '/zones/regions.geojson')
        starting_zoom = 5
        fields = ['name', 'zone_type', 'sum']
        aliases = ['Name', 'Zone Type', query[-1].upper()+' Crime Frequency']
    data['name'] = data['name'].str.upper()
    # for_plotting = results.merge(data, left_on = 'name', right_on = 'name')
    merged2 = data.merge(results,on="name")
    # merged = gpd.GeoDataFrame(for_plotting)
    # geo_j = merged.to_json()

    # finding coordinates of starting location
    if query[0].lower() != 'all':
        loc = Nominatim(user_agent="GetLoc")
        try:
            getLoc = loc.geocode(query[0]+', WA, Australia')
            starting_point = [getLoc.latitude, getLoc.longitude]
        except: 
        # starting location coordinates [lat, long] set to Perth if no coordinates found
            starting_point = [-32, 116]
    else:
        starting_point = [-25.32805556, 122.29833333]
    
    # creating a map object for choropleth map
    choropleth = folium.Map(
        location=starting_point,
        tiles='https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        zoom_start=starting_zoom,
        max_zoom=15,
        min_zoom=3,
        attr='Crime Heatmap')

    #Creating choropleth map object with key on suburb name
    folium.Choropleth(
        geo_data = merged2, #Assign geo_data to your geojson file
        name = "WA Crime Heat Map",
        data = merged2, #Assign dataset of interest
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

    # Creating popup tooltip object
    NIL = folium.features.GeoJson(
        merged2,
        style_function=style_function, 
        control=False,
        highlight_function=highlight_function, 
        tooltip=folium.features.GeoJsonTooltip(
            fields=fields,
            aliases=aliases,
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")))

    #Adding tooltip object to the map
    choropleth.add_child(NIL)
    choropleth.keep_in_front(NIL)
    folium.LayerControl().add_to(choropleth)
    
    if query[0].lower() != 'all':
        if isinstance(anomalies, pd.DataFrame):
            anomaly_locations = list(anomalies['name'].unique())
            final_df =  anomalies[['name', 'year', 'observation', 'mean']]
            final_df.rename(columns={'year': 'Year', 'observation': 'Observed Crime Numbers', 'mean': 'Mean Crime Numbers'}, inplace=True)
            try:
                for i in anomaly_locations:
                    if query[1] == 'suburb' or 'station':
                        with open(r'{}'.format(COORDINATES)) as f:
                            coordinates = json.load(f)
                    if query[1] == 'district':
                        with open(r'{}'.format(STATIONS)) as f:
                            coordinates = json.load(f)
                    if query[1] == 'region':
                        with open(r'{}'.format(DISTRICTS)) as f:
                            coordinates = json.load(f)
                    coordinates = dict(coordinates)
                    location = coordinates[i.lower()]
                    if location != '':
                        html_df = final_df.loc[final_df['name'] == i]
                        html_df.index = np.arange(1, len(html_df) + 1)
                        html = html_df.to_html(classes=
                            "table table-striped table-hover table-condensed table-responsive")
                    # iframe = folium.IFrame(html=html,
                    #        width=100,
                    #        height=100)
                        folium.Marker(
                            location=location, 
                            icon=folium.Icon(color="blue",icon="map-pin", prefix='fa'),
                            popup=folium.Popup(html),
                        ).add_to(choropleth)
            except ValueError:
                print('hi')

    choropleth.save('generated_map.html')
    return plot
    
def main():
    for file in FILES:
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