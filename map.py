import os
import csv
import numpy as np
import pandas as pd
import geopandas as gpd
import json
#import folium
#import seaborn as sns
#import scipy as sp
#import matplotlib.pyplot as plt
#import boundaries

def check_text(textfile): #to check if file exists
    if not os.path.isfile(textfile): 
        return None
    else:
        return True

def file_prep(datafile, geojson, xlsx_csv, coordinates):
    #prepare csv file
    #consider if filling missing years & crimes is necessary for plotting & analysis
    with open(datafile, 'r') as file:
        data = list(csv.reader(file, delimiter = ','))
        headers, data = data[0], data[1:]
        headers = [header.lower() for header in headers]
    for line in data:
        for i in range(0,len(line)):
            if line[i] == '':
                line[i] = '0'
    data = pd.DataFrame(data)
    data.columns = headers
    data['suburb'] = data['suburb'].str.lower()
    data['website category names'] = data['website category names'].str.lower()
    data = data.apply(pd.to_numeric, errors='ignore')

    #prepare geojson file
    init_gda = gpd.read_file(geojson)
    gda = init_gda[{'name':init_gda['name'],'geometry':init_gda['geometry']}]
    gda['name'] = gda['name'].str.lower()

    #prepare localities file
    localities = pd.read_csv(xlsx_csv)
    localities_header = np.char.lower(localities.columns.values.astype(str))
    localities.columns = localities_header
    for header in localities_header:
        localities[header] = localities[header].str.lower()

    #prepare coordinates from final_data.json
    with open(coordinates, 'r') as temp:
        boundaries = json.loads(temp.read())
    #print(boundaries['suburbs']['west lyons river'])
    #print(boundaries['stations']['albany'])
    #print(boundaries['districts']['armadale'])
    #print(boundaries['regions']['metropolitan region north'])

    return (data, gda.sort_values(by='name'), localities, boundaries)

def selector_options(data):
    #making a list of places
    places = data['suburb'].tolist()
    #making a list for the crimes occurred
    crimes = data['website category names'].drop_duplicates().tolist()
    #making a list of all the dates
    years = data['year'].drop_duplicates().sort_values().tolist()
    #Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec -> ignore this for now
    #Jul, Aug, Sep, Oct, Nov, Dec, Jan, Feb, Mar, Apr, May, Jun -> focus on this
    #with months, 2d arrays?
    months = [['jul'],['aug'],['sep'],['oct'],['nov'],['dec'],['jan'],['feb'],['mar'],['apr'],['may'],['jun']]
    quarters = [['jul-sep'],['oct-dec'],['jan-mar'],['apr-jun']]
    return places, crimes, years, months, quarters

def selector_options_expanded(data, localities):
    #making a list of places
    places = ['all'] + data['suburb'].drop_duplicates().tolist()
    #making a list of zone types
    types = ['suburb', 'station', 'district', 'region']
    suburb = localities['sub_txt'].drop_duplicates().sort_values().tolist()
    station = localities['station'].drop_duplicates().sort_values().tolist()
    district = localities['district'].drop_duplicates().sort_values().tolist()
    region = localities['region'].drop_duplicates().sort_values().tolist()
    #making a list for the crimes occurred
    crimes = ['all'] + data['website category names'].drop_duplicates().tolist()
    #making a list of all the dates
    years = ['all'] + data['year'].drop_duplicates().sort_values().tolist()
    #Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec -> ignore this for now
    #Jul, Aug, Sep, Oct, Nov, Dec, Jan, Feb, Mar, Apr, May, Jun -> focus on this
    #with months, 2d arrays?
    #q1 == jul + aug + sep, q2 == oct + nov + dec, q3 == jan + feb + mar, q4 == apr + may + jun
    distribution = ['all', 'jul','aug','sep','oct','nov','dec','jan','feb','mar','apr','may', 'jun', 'q1', 'q2', 'q3', 'q4']
    return places, types, suburb, station, district, region, crimes, years, distribution

def data_input():
    class selector:

        def __init__(self, locality, offence, date):
            self.locality = locality
            self.offence = offence
            self.date = date
    
    x,y,z = input('{} {} {}').split(',')
    selectors = selector(x.strip().lower(), y.strip().lower(), z.strip().lower())
    return selectors

def data_input_extended():
    #class localities:
    #    def __init__(self, suburb, station, district, region):
    #        self.suburb = suburb
    #        self.station = station
    #        self.district = district
    #        self.region = region

    #class dates:
    #    def __init__(self, year, month, quarter):
    #        self.year = year
    #        self.month = month
    #        self.quarter = quarter

    class new_selector:
        def __init__(self, name = '', locality = 'all', year = 'all', distribution = 'all', offence = 'all'):
            #indicates name of suburb, station, district or region
            self.name = name
            #indicates either specific suburb, police stations, districts or regions
            self.locality = locality
            #indicates year spread
            self.year = year
            #indicates months or quarters
            self.distribution = distribution
            #indicates specific offence
            self.offence = offence
    print('The input format is name, locality, year, distribution, offence')
    v,w,x,y,z = input('{} {} {} {} {}').split(',')

    selectors = new_selector(v.strip().lower(), w.strip().lower(),x.strip().lower(), y.strip().lower(), z.strip().lower())
    return selectors


#def churning_initial(data, selectors):
    #all,all,all should be the default selectors
    #afterwards should it be every single selector change rerun this function?
    #if so, how to make it a recurring function?
    output = data[data.columns[[0, 1, 2, -1]]]
    if (selectors.name == 'all' and selectors.offence == 'all' and selectors.year == 'all'): #initial heatmap
        #all, all, all
        ##rethink this area how to make new dataframe with [locality, sum of crimes (regardless of crime and date), coordinates]
        output = output.groupby(['suburb'])['annual'].sum()
        places = places[1:]
        output = pd.DataFrame({'suburb': places, 'sum': list(output)})
    elif (selectors.name != 'all' and selectors.offence == 'all' and selectors.year == 'all'): #for detailed suburb view
        #locality, all, all
        output = output.loc[output['suburb'] == selectors.name]
    elif (selectors.name == 'all' and selectors.offence != 'all' and selectors.year == 'all'): #for overall crime numbers
        #all, crime, all
        ##should we consider splitting the sums into individual localities?
        output = output.loc[output['website category names'] == selectors.offence]
    elif (selectors.name == 'all' and selectors.offence == 'all' and selectors.year != 'all'): #for crimes committed over certain year_range
        #all, all, year_range
        ##should we consider splitting the sums into individual localities?
        output = output.loc[output['year'] == selectors.year]
    elif (selectors.name != 'all' and selectors.offence != 'all' and selectors.year == 'all'):
        #locality, crime, all
        output = output.loc[output['suburb'] == selectors.name]
        output = output.loc[output['website category names'] == selectors.offence]
    elif (selectors.name == 'all' and selectors.offence != 'all' and selectors.year != 'all'):
        #all, crime, year_range
        output = output.loc[output['website category names'] == selectors.offence]
        output = output.loc[output['year'] == selectors.year]
    elif (selectors.name != 'all' and selectors.offence == 'all' and selectors.year != 'all'):
        #locality, all, year_range
        output = output.loc[output['suburb'] == selectors.name]
        output = output.loc[output['year'] == selectors.year]
    elif (selectors.name != 'all' and selectors.offence != 'all' and selectors.year != 'all'): #too specific?
        #locality, crime, year_range
        output = output.loc[output['suburb'] == selectors.name]
        output = output.loc[output['website category names'] == selectors.offence]
        output = output.loc[output['year'] == selectors.year]
    return output

def churning_simplified(data, places, selectors):
    #all,all,all should be the default selectors
    #afterwards should it be every single selector change rerun this function?
    #if so, how to make it a recurring function?
    output = data[data.columns[[0, 1, 2, -1]]]
    if selectors.name != 'all' or selectors.offence != 'all' or selectors.year != 'all':
        if selectors.name != 'all':
            output = output.loc[output['suburb'] == selectors.name]
        if selectors.offence != 'all':
            output = output.loc[output['website category names'] == selectors.offence]
        if selectors.year != 'all':
            output = output.loc[output['year'] == selectors.year]
    elif (selectors.name == 'all' and selectors.offence == 'all' and selectors.year == 'all'): #initial heatmap
        #all, all, all
        ##rethink this area how to make new dataframe with [locality, sum of crimes (regardless of crime and date), coordinates]
        output = output.groupby(['suburb'])['annual'].sum()
        places = places[1:]
        output = pd.DataFrame({'suburb': places, 'sum': list(output)})
    return output

def churning_complicated(data, places, years, distribution, selectors):
    #['jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'q1', 'q2', 'q3', 'q4']
    col_num = np.array([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
    places = places[1:]
    years = years[1:]
    distribution = distribution[1:]
    years_list = []
    col_list = []
    output = data.rename(columns = {'annual': 'sum'})
    print(output)
    initial = [0, 1, 2]
    q0 = []
    q1 = [3, 4, 5]
    q2 = [6, 7, 8]
    q3 = [9, 10, 11]
    q4 = [12, 13, 14]

    if selectors.year != all:
        temp1, temp2 = selectors.year.split('-')
        temp1 = str(int(temp1[-2:]) + 1)
        [years_list.append(i) for i in years if (temp1 <= i[-2:] and i[-2:] <= temp2)]
        output = output[output['year'].isin(years_list)]

    if selectors.distribution != 'all':
        if '-' in selectors.distribution:
            temp1, temp2 = selectors.distribution.split('-')
            if 'q' in temp1:
                temp = range(locals()[temp1][0], locals()[temp2][-1] + 1)
                [q0.append(i) for i in temp]
            elif 'q' not in temp1:
                temp = distribution[distribution.index(temp1):distribution.index(temp2) + 1]
                [q0.append(distribution.index(i) + 3) for i in temp]
        elif selectors.distribution == 'q1':
            q0 = q1
        elif selectors.distribution == 'q2':
            q0 = q2
        elif selectors.distribution == 'q3':
            q0 = q3
        elif selectors.distribution == 'q4':
            q0 = q4
        elif len(list(selectors.distribution)) == 3:
            q0 = [distribution.index(selectors.distribution) + 3]
        output = output[output.columns[initial + q0]]

    if selectors.name != 'all' or selectors.offence != 'all':
        if selectors.name != 'all':
            output = output.loc[output['suburb'] == selectors.name]
        if selectors.offence != 'all':
            output = output.loc[output['website category names'] == selectors.offence]
    elif (selectors.name == 'all' and selectors.offence == 'all'):
        ##rethink this area how to make new dataframe with [locality, sum of crimes (regardless of crime and date), coordinates]
        output = output.groupby(['suburb'])['annual'].sum()
        output = pd.DataFrame({'suburb': places, 'sum': list(output)})

    col_num = np.array(q0) - 3
    [col_list.append(distribution[i]) for i in col_num]
    output['sum'] = output[col_list].sum(axis=1)
    output = output[output.columns[[0, 1, 2, -1]]]

    '''group data by zone type
    if year not 'all':
        filter out invalid years
    if distribution not 'all'
        filter out invalid months and quarters
    if offence not 'all':
        filter out invalid offence'''
    
    return output

def churning_expanded(data, places, years, distribution, selectors):
    #selectors should include [suburb/station/district/region, crime_type, year_range, distribution]
    ##distribution includes months and quarters
    ###for year_range and distribution, focus on fixed ranges or explore custom ranges?
    if selectors.year not in years or selectors.distribution != 'all':
        output = churning_complicated(data, places, years, distribution, selectors)
    elif selectors.year in years and selectors.distribution == 'all':
        output = churning_simplified(data, places, selectors)
    return output

def png_plots():
    #time series analysis
    ##full range of 2010-21, or custom? no standardization tho...
    png = []
    return png

def statistics():
    #mean, median, mode
    ##standard deviation, standard error
    ###binomial, poisson, normal distribution and analysis? significant or not?
    stats = []
    return stats

def main():
    #first section of code prepares/checks the files
    datafile = 'Locality_Data_Filtered (from Quart Website Rep Mar213-2.csv'
    geojson = r'Localities_LGATE_234_WA_GDA2020_Public.geojson'
    xlsx_csv = 'Suburb Locality.csv'
    coordinates = 'final_data.json'
    if check_text(datafile) == None:
        return None
    if check_text(geojson) == None:
        return None
    if check_text(xlsx_csv) == None:
        return None
    if check_text(coordinates) == None:
        return None
    #ignore gda for now
    data, gda, localities, boundaries = file_prep(datafile, geojson, xlsx_csv, coordinates)

    #places, crimes, years, months, quarters = selector_options(data)
    places, types, suburb, station, district, region, crimes, years, distribution = selector_options_expanded(data, localities)

    #maybe the function just runs through each new iteration of selectors when the selectors are changed on the UI
    #selectors = data_input()
    selectors = data_input_extended()
    '''if (selectors.locality not in types and selectors.name not in locals()[selectors.locality]):
        return None
    if selectors.year not in years:
        return None
    if selectors.distribution not in distribution:
        return None
    if selectors.offence not in crimes:
        return None'''

    #when preparing the data, collect the queries in the selectors format first
    #after error-checking them, filter from data to get only the required localities
    #after filtering, sum according to distribution and years where necessary
    #after sum, grab coordinates from boundaries to complete the variable

    #result = churning_simplified(data, places, selectors)
    ##start classifying based on specific localities and names
    result = churning_expanded(data, places, years, distribution, selectors)

    print(result)

    '''print(data.shape)
    print(localities.shape)
    print(len(boundaries['suburbs']))
    print(len(boundaries['stations']))
    print(len(boundaries['districts']))
    print(len(boundaries['regions']))'''

    #return ****.html, statistical_info

if __name__ == '__main__':
    main()

#signature [name, zone_type, year_range, distribution, crime]