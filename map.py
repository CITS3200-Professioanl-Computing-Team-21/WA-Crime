import os
import csv
import numpy as np
import pandas as pd
import geopandas as gpd
#import folium
#import seaborn as sns
#import scipy as sp
#import matplotlib.pyplot as plt

def check_text(textfile): #to check if file exists
    if not os.path.isfile(textfile): 
        return None
    else:
        return True

def file_prep(datafile, geojson, xlsx_csv):
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

    return (data, gda.sort_values(by='name'), localities)

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

def data_input():
    #class new_selector:
    #    def __init__(self, locality, offence, year, distribution):
            #indicates either specific suburb, police stations, districts or regions
    #        self.locality = locality
            #indicates specific offence
    #        self.offence = offence
            #indicates year spread
    #        self.year = year
            #indicates months or quarters
    #        self.distribution = distribution

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
    output = []
    class selector:

        def __init__(self, locality, offence, date):
            self.locality = locality
            self.offence = offence
            self.date = date
    
    x,y,z = input('{} {} {}').split(',')
    selectors = selector(x.strip().lower(), y.strip().lower(), z.strip().lower())
    return (selectors, output)

def churning_9(data, output, selectors):
    #all,all,all should be the default selectors
    #afterwards should it be every single selector change rerun this function?
    #if so, how to make it a recurring function?
    if (selectors.locality == 'all' and selectors.offence == 'all' and selectors.date == 'all'): #initial heatmap
        #all, all, all
        ##rethink this area how to make new dataframe with [locality, sum of crimes (regardless of crime and date), coordinates]
        output = data.groupby(['suburb'])['annual'].sum()
    elif (selectors.locality != 'all' and selectors.offence == 'all' and selectors.date == 'all'): #for detailed suburb view
        #locality, all, all
        temp = data.loc[data['suburb'] == selectors.locality]
        output = temp.groupby(['suburb', 'website category names', 'year'])['annual'].sum()
    elif (selectors.locality == 'all' and selectors.offence != 'all' and selectors.date == 'all'): #for overall crime numbers
        #all, crime, all
        ##should we consider splitting the sums into individual localities?
        output = data.groupby(['website category names'])['annual'].sum()
    elif (selectors.locality == 'all' and selectors.offence == 'all' and selectors.date != 'all'): #for crimes committed over certain year_range
        #all, all, year_range
        ##should we consider splitting the sums into individual localities?
        output = data.groupby(['year'])['annual'].sum()
    elif (selectors.locality != 'all' and selectors.offence != 'all' and selectors.date == 'all'):
        #locality, crime, all
        temp = data.loc[data['suburb'] == selectors.locality]
        temp1 = temp.loc[temp['website category names'] == selectors.offence]
        output = temp1[temp1.columns[[0, 1, 2, -1]]]
    elif (selectors.locality == 'all' and selectors.offence != 'all' and selectors.date != 'all'):
        #all, crime, year_range
        temp = data.loc[data['website category names'] == selectors.offence]
        temp1 = temp.loc[temp['year'] == selectors.date]
        output = temp1[temp1.columns[[0, 1, 2, -1]]]
    elif (selectors.locality != 'all' and selectors.offence == 'all' and selectors.date != 'all'):
        #locality, all, year_range
        temp = data.loc[data['suburb'] == selectors.locality]
        temp1 = temp.loc[temp['year'] == selectors.date]
        output = temp1[temp1.columns[[0, 1, 2, -1]]]
    elif (selectors.locality != 'all' and selectors.offence != 'all' and selectors.date != 'all'): #too specific?
        #locality, crime, year_range
        temp = data.loc[data['suburb'] == selectors.locality]
        temp1 = temp.loc[temp['website category names'] == selectors.offence]
        temp2 = temp1.loc[temp1['year'] == selectors.date]
        output = temp2[temp2.columns[[0, 1, 2, -1]]]
    return output

#def churning_10(data, output, selectors):
    #selectors should include [suburb/station/district/region, crime_type, year_range, distribution]
    ##distribution includes months and quarters
    ###for year_range and distribution, focus on fixed ranges or explore custom ranges?
    return output

def main():
    datafile = 'Locality_Data_Filtered (from Quart Website Rep Mar213-2.csv'
    geojson = r'Localities_LGATE_234_WA_GDA2020_Public.geojson'
    xlsx_csv = 'Suburb Locality.csv'
    if check_text(datafile) == None:
        return None
    if check_text(geojson) == None:
        return None
    if check_text(xlsx_csv) == None:
        return None
    #beginning two lines prepares/checks the files and creates the selector options
    data, gda, localities = file_prep(datafile, geojson, xlsx_csv)
    places, crimes, dates, months, quarters = selector_options(data)
    #maybe the function just runs through each new iteration of selectors when the selectors are changed on the UI
    selectors, output = data_input()
    result = churning_9(data, output, selectors)
    print(dates)

if __name__ == '__main__':
    main()