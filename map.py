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

def check_text(textfile):
    #to check if file exists
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
    data = data.rename(columns = {'annual': 'sum'})
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
    localities = localities.rename(columns = {'sub_txt': 'suburb'})

    #prepare coordinates from final_data.json
    with open(coordinates, 'r') as temp:
        boundaries = json.loads(temp.read())
    #print(boundaries['suburbs']['west lyons river'])
    #print(boundaries['stations']['albany'])
    #print(boundaries['districts']['armadale'])
    #print(boundaries['regions']['metropolitan region north'])

    return (data, gda.sort_values(by='name'), localities, boundaries)

def selector_options_expanded(data, localities):
    #making a list of places
    places = ['all'] + data['suburb'].drop_duplicates().tolist()
    #making a list of zone types
    types = ['all', 'suburb', 'station', 'district', 'region']
    suburb = ['all'] + localities['suburb'].drop_duplicates().sort_values().tolist()
    station = ['all'] + localities['station'].drop_duplicates().sort_values().tolist()
    district = ['all'] + localities['district'].drop_duplicates().sort_values().tolist()
    region = ['all'] + localities['region'].drop_duplicates().sort_values().tolist()
    #making a list for the crimes occurred
    crimes = ['all'] + data['website category names'].drop_duplicates().tolist()
    #making a list of all the dates
    years = ['all'] + data['year'].drop_duplicates().sort_values().tolist()
    #Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec -> ignore this for now
    #Jul, Aug, Sep, Oct, Nov, Dec, Jan, Feb, Mar, Apr, May, Jun -> focus on this
    #q1 == jul + aug + sep, q2 == oct + nov + dec, q3 == jan + feb + mar, q4 == apr + may + jun
    distribution = ['all', 'jul','aug','sep','oct','nov','dec','jan','feb','mar','apr','may', 'jun', 'q1', 'q2', 'q3', 'q4']
    return places, types, suburb, station, district, region, crimes, years, distribution

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

def churning_final(data, localities, years, distribution, selectors):
    #['jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'q1', 'q2', 'q3', 'q4']
    col_num = np.array([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
    years = years[1:]
    distribution = distribution[1:]
    years_list = []
    col_list = []
    initial = [0, 1, 2]
    q0 = []
    q1 = [3, 4, 5]
    q2 = [6, 7, 8]
    q3 = [9, 10, 11]
    q4 = [12, 13, 14]

    names_data = localities.loc[localities[selectors.locality] == selectors.name]
    names_list = names_data['suburb'].drop_duplicates().sort_values().tolist()
    names_cut = data[data['suburb'].isin(names_list)]

    if selectors.year == 'all':
        selectors.year = '2010-21'
    temp1, temp2 = selectors.year.split('-')
    temp1 = str(int(temp1[-2:]) + 1)
    [years_list.append(i) for i in years if (temp1 <= i[-2:] and i[-2:] <= temp2)]
    output = names_cut[names_cut['year'].isin(years_list)]

    #print('error1')
    #print(output)

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
    elif selectors.distribution == 'all':
        q0 = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    output = output[output.columns[initial + q0]]

    #print('error2')
    #print(output)

    col_num = np.array(q0) - 3
    [col_list.append(distribution[i]) for i in col_num]
    output['sum'] = output[col_list].sum(axis=1)
    output = output[output.columns[[0, 1, 2, -1]]]
    names_list = output['suburb'].drop_duplicates().sort_values().tolist()

    #print('error3')
    #print(output)

    if selectors.offence != 'all':
        output = output.loc[output['website category names'] == selectors.offence]
        output = output.rename(columns = {'suburb': 'name'})
    elif selectors.offence == 'all':
        output = output.groupby(['suburb'])['sum'].sum()
        output = pd.DataFrame({'name': names_list, 'sum': list(output)})

    #print('error4')
    #print(output)

    columns = output['name'].drop_duplicates().sort_values().tolist()
    sums = list(output.groupby(['name'])['sum'].sum())
    result = pd.DataFrame({'name':columns, 'sum':sums})
    result = result.set_index('name').reindex(names_list).reset_index()
    result['sum'] = result['sum'].fillna(0)
    result = result.astype(int, errors='ignore')

    #print('error5')
    #print(result)
    
    return result

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
    #to ignore warning [[]], code will run as per normal
    pd.options.mode.chained_assignment = None

    #first section of code prepares/checks the files
    #datafile = 'Locality_Data_Filtered (from Quart Website Rep Mar213-2.csv'
    datafile = 'crime.csv'
    geojson = r'Localities_LGATE_234_WA_GDA2020_Public.geojson'
    xlsx_csv = 'Suburb Locality.csv'
    coordinates = 'final_data.json'
    sum_list = []
    if check_text(datafile) == None:
        return None
    if check_text(geojson) == None:
        return None
    if check_text(xlsx_csv) == None:
        return None
    if check_text(coordinates) == None:
        return None
    #ignore gda and boundaries for now
    data, gda, localities, boundaries = file_prep(datafile, geojson, xlsx_csv, coordinates)

    #places, crimes, years, months, quarters = selector_options(data)
    places, types, suburb, station, district, region, crimes, years, distribution = selector_options_expanded(data, localities)

    #maybe the function just runs through each new iteration of selectors when the selectors are changed on the UI
    #make the function receive data instead of input data

    #when preparing the data, collect the queries in the selectors format first
    #after error-checking them, filter from data to get only the required localities
    #after filtering, sum according to distribution and years where necessary
    #after sum, grab coordinates from boundaries to complete the variable

    #step1: filter based on years
    #step2: filter based on distribution
    #step3: filter based on offences
    #step4: sum counts based on name and zone_type

    #run these queries
    ## [all, suburb, year_range, distribution, crime] # display all suburbs
    ## [all, station, year_range, distribution, crime] # display all stations
    ## [all, district, year_range, distribution, crime] # display all districts
    ## [all, region, year_range, distribution, crime] # display all the regions
    selectors = data_input_extended()
    if selectors.locality == 'all':
        selectors.name = 'all'
        selectors.locality = 'suburb'
    if selectors.year == 'all':
        selectors.year = '2010-21'

    if selectors.name not in locals()[selectors.locality]:
        print('name failed')
        return None
    if selectors.locality not in types:
        print('locality failed')
        return None
    if (selectors.year.split('-')[0] + '-' + str(int(selectors.year.split('-')[0][2:]) + 1)) not in years:
        print('year failed')
        return None
    if (selectors.distribution.split('-')[0]) not in distribution:
        print('distribution failed')
        return None
    if selectors.offence not in crimes:
        print('offence failed')
        return None

    if selectors.name != 'all':
        if selectors.locality == 'suburb' or selectors.locality == 'station':
            result = churning_final(data, localities, years, distribution, selectors)
        elif selectors.locality == 'district':
            name_data = localities.loc[localities[selectors.locality] == selectors.name]
            name_list = name_data['station'].drop_duplicates().sort_values().tolist()
            selectors.locality = 'station'
            for name in name_list:
                selectors.name = name
                temp_result = churning_final(data, localities, years, distribution, selectors)
                sum_list.append(temp_result['sum'].sum())
            result = pd.DataFrame({'name': name_list, 'sum': list(sum_list)})
        elif selectors.locality == 'region':
            name_data = localities.loc[localities[selectors.locality] == selectors.name]
            name_list = name_data['district'].drop_duplicates().sort_values().tolist()
            selectors.locality = 'district'
            for name in name_list:
                selectors.name = name
                temp_result = churning_final(data, localities, years, distribution, selectors)
                sum_list.append(temp_result['sum'].sum())
            result = pd.DataFrame({'name': name_list, 'sum': list(sum_list)})
    elif selectors.name == 'all':
        name_list = locals()[selectors.locality]
        name_list.remove('unknown')
        name_list.remove('all')
        for name in name_list:
            selectors.name = name
            temp_result = churning_final(data, localities, years, distribution, selectors)
            sum_list.append(temp_result['sum'].sum())
        result = pd.DataFrame({'name': name_list, 'sum': list(sum_list)})

    print(result)
    return result

    #return ****.html, statistical_info

if __name__ == '__main__':
    main()

#signature [name, zone_type, year_range, distribution, crime]