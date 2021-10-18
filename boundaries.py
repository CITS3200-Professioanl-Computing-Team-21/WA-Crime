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

# directory path
PATH = os.getcwd() 

# constant variables containing main data file names
CRIME = 'crime.csv'
LANDGATE = 'Localities_LGATE_234_WA_GDA2020_Public.geojson'
ZONES = 'Suburb Locality.csv'
FILES = [CRIME, LANDGATE, ZONES]

# constant variables containing centroid file names
COORDINATES_C = PATH + '/centroids/coordinates.json'
STATIONS_C = PATH + '/centroids/station_centroids.json'
DISTRICTS_C = PATH + '/centroids/district_centroids.json'
REGIONS_C = PATH + '/centroids/region_centroids.json'

# constant variables containing geojson file names
SUBURBS_G = PATH + '/zones/suburbs.geojson'
STATIONS_G = PATH + '/zones/stations.geojson'
DISTRICTS_G = PATH + '/zones/districts.geojson'
REGIONS_G = PATH + '/zones/regions.geojson'

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

# function - to determine locations that may not be present across all data files
def check_naming(landgate_locations, crime_locations, zones):
    for location in crime_locations:
        # locations in CRIME that are not present in ZONES
        missing1 = [location for location in crime_locations if location not in zones['suburbs']]
        # locations in CRIME that are not present in LANDGATE
        missing2 = [location for location in crime_locations if location not in landgate_locations]
    changes = []
    if not missing1:
        if missing2: 
            for location in missing2:
                # matches missing locations which are mismatched but have very similar spelling
                highest = process.extractOne(location, landgate_locations) # only extracts the matched location with the highest similarity
                landgate_location, score = highest[0], highest[1]
                if landgate_location not in crime_locations and score > 85: # only locations with a similarity score of >85 are chosen
                    changes.append((location, landgate_location))
                    missing2.remove(location)
    return (missing2, changes)

# function - to determine whether the matched missing locations are feasible
def missing_locations(zones_data, zones, missing2):
    station_coordinates = {}
    # loop to determine the station coordinates of each station
    for station in zones['stations']:
        # calling the Nominatim tool from the Geopy API
        loc = Nominatim(user_agent="GetLoc") 
        # entering the location name and obtaining coordinates from API
        getLoc = loc.geocode(station+', WA, Australia')
        station_coordinates[station] = (getLoc.latitude, getLoc.longitude)
    missing_landgate = {}
    # loop to determine the coordinates of each missing location and to check whether it falls within a 200km radius of its designated station
    for location in missing2:
        loc = Nominatim(user_agent="GetLoc") 
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

# function - for the matched locations that are deemed feasible, that location is classfied into a boundary from LANDGATE boundaries
def assign_missing_boundaries(missing_landgate, landgate_data, changes, crime_locations):
    for location in missing_landgate:
        point = Point(missing_landgate[location][1], missing_landgate[location][0])
        for i in landgate_data['features']:
            polygon = shape(i['geometry'])
            landgate_location = i['properties']['name'].lower()
            if polygon.contains(point) and landgate_location not in crime_locations:
                changes.append((location, landgate_location))
    return (changes)

# function - to generate the final zoning and centroid files required for plotting
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
                # combining all of the boundaries in the specific zone type to form one boundary
                polygon = unary_union(polygons).simplify(tolerance=0.001)
                # obtaining lat, lng of the centre point of the generated boundaries
                try:
                    x = polygon.centroid.x
                    y = polygon.centroid.y
                except IndexError:
                    x = ''
                    y = ''
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
    selected_features.to_file(PATH + '/zones/suburbs.geojson', driver="GeoJSON")

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

# function - to generate the heat map and plot anomalies
def choropleth(query):
    # check for new line character
    if query[0][-1] == '\n':
        query[0] = query[0][:-1]

    # loading centre points (centroids) of all zone types
    with open(r'{}'.format(COORDINATES_C)) as f:
        coordinates_suburbs = json.load(f)
    with open(r'{}'.format(STATIONS_C)) as f:
        coordinates_stations = json.load(f)
    with open(r'{}'.format(DISTRICTS_C)) as f:
        coordinates_districts = json.load(f)
    with open(r'{}'.format(REGIONS_C)) as f:
        coordinates_regions = json.load(f)

    # obtaining query results from filter.py
    results, anomalies, plot = filter.filter(query[0], query[1], query[2], query[3], query[4])
    results['name'] = results['name'].str.upper()
    # adding another column for log transformed data
    results['log'] = np.log(results['sum']+1)

    if (query[1] == 'suburb') or (query[1] == 'station' and query[0].lower() != 'all'):
        data = gpd.read_file(SUBURBS_G)
        starting_zoom = 12
        fields = ['name', 'postcode', 'land_area','sum']
        aliases = ['Name', 'Postcode', 'Land Area', query[-1].upper()+' Crime Frequency']
    if (query[1] == 'district' and query[0].lower() != 'all') or (query[1] == 'station' and query[0].lower() == 'all'):
        data = gpd.read_file(STATIONS_G)
        starting_zoom = 9
        fields = ['name', 'zone_type', 'sum']
        aliases = ['Name', 'Zone Type', query[-1].upper()+' Crime Frequency']
    if (query[1] == 'region' and query[0].lower() != 'all') or (query[1] == 'district' and query[0].lower() == 'all'):
        data = gpd.read_file(DISTRICTS_G)
        starting_zoom = 5
        fields = ['name', 'zone_type', 'sum']
        aliases = ['Name', 'Zone Type', query[-1].upper()+' Crime Frequency']
    if (query[1] == 'region' and query[0].lower() == 'all'):
        data = gpd.read_file(REGIONS_G)
        starting_zoom = 5
        fields = ['name', 'zone_type', 'sum']
        aliases = ['Name', 'Zone Type', query[-1].upper()+' Crime Frequency']
    
    if query[0] == 'all':
        starting_zoom = 5

    data['name'] = data['name'].str.upper()
    # merging the geodata and aggregated data
    merged = data.merge(results,on="name")

    # finding coordinates of starting location
    if query[0].lower() != 'all':
        if query[1] == 'suburb':
            coordinates = coordinates_suburbs
        if query[1] == 'station':
            coordinates = coordinates_stations
        if query[1] == 'district':
            coordinates = coordinates_districts
        if query[1] == 'region':
            coordinates = coordinates_regions 
        try:
            loc = coordinates[query[0]]
            starting_point = [loc[0], loc[1]]
        except: 
        # starting location coordinates [lat, long] set to Perth if no coordinates found
            starting_point = [-32, 116]
    else:
        # starting location coordinates [lat, long] set to centre of WA if 'all' query
        starting_point = [-25.32805556, 122.29833333]
    
    # creating a map object for choropleth map
    choropleth = folium.Map(
        location=starting_point,
        tiles='https://server.arcgisonline.com/arcgis/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        zoom_start=starting_zoom,
        max_zoom=15,
        min_zoom=3,
        attr='Crime Heatmap')

    # creating choropleth map object with key on suburb name
    folium.Choropleth(
        geo_data = merged, # assign geo_data to your geojson file
        name = "WA Crime Heat Map",
        data = merged, # assign dataset of interest
        columns = ['name', 'log'], # assign columns in the dataset for plotting
        key_on = 'feature.properties.name', # assign the key that geojson uses to connect with dataset
        fill_color = 'YlOrRd',
        fill_opacity = 0.4,
        line_opacity = 0.5,
        bins = 9,
        legend_name = 'legend').add_to(choropleth)
    
    # creating style_function
    style_function = lambda x: {
                    'fillColor': '#ffffff', 
                    'color':'#000000', 
                    'fillOpacity': 0.1, 
                    'weight': 0.1}

    # creating highlight_function
    highlight_function = lambda x: {
                    'fillColor': '#000000', 
                    'color':'#000000', 
                    'fillOpacity': 0.50, 
                    'weight': 0.1}

    # creating popup tooltip object
    NIL = folium.features.GeoJson(
        merged,
        style_function=style_function, 
        control=False,
        highlight_function=highlight_function, 
        tooltip=folium.features.GeoJsonTooltip(
            fields=fields,
            aliases=aliases,
            style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")))

    # adding tooltip object to the map
    choropleth.add_child(NIL)
    choropleth.keep_in_front(NIL)
    folium.LayerControl().add_to(choropleth)
    
    # adding anomalies to the map
    if query[0].lower() != 'all':
        if isinstance(anomalies, pd.DataFrame):
            anomaly_locations = list(anomalies['name'].unique())
            final_df =  anomalies[['name', 'year', 'observation', 'mean']]
            final_df.rename(columns={'year': 'Year', 'observation': 'Observed Crime Numbers', 'mean': 'Mean Crime Numbers'}, inplace=True)
            try:
                for i in anomaly_locations:
                    if query[1] == 'suburb' or 'station':
                        coordinates = coordinates_suburbs
                    if query[1] == 'district':
                        coordinates = coordinates_stations
                    if query[1] == 'region':
                        coordinates = coordinates_districts
                    coordinates = dict(coordinates)
                    location = coordinates[i.lower()]
                    if location != '':
                        html_df = final_df.loc[final_df['name'] == i]
                        html_df.index = np.arange(1, len(html_df) + 1)
                        html = html_df.to_html(classes=
                            "table table-striped table-hover table-condensed table-responsive")
                        folium.Marker(
                            location=location, 
                            icon=folium.Icon(color="blue",icon="map-pin", prefix='fa'),
                            popup=folium.Popup(html),
                        ).add_to(choropleth)
            except:
                print('anomaly error')

    choropleth.save('generated_map.html')
    return plot
    
def main():
    # many functions have been commented out as they are not required for the running of the app
    # they were only required for the generation of the mapping data files
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