#import folium
#from html2image import Html2Image
#import matplotlib.pyplot as plt
#m = folium.Map(location=[-31.9535132, 115.85704710000005], zoom_start=12)
#m.save('test.html')
#hti = Html2Image()
#hti.screenshot(html_file='test.html', save_as='out.png')

#import folium
import csv
import numpy as np
import pandas as pd
import geopandas as gpd
#import seaborn as sns
#import scipy as sp
#import matplotlib.pyplot as plt

def file_prep(datafile, geojson, xlsx):

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

    #prepare geojson file
    init_gda = gpd.read_file(geojson)
    gda = init_gda[{'name':init_gda['name'],'geometry':init_gda['geometry']}]
    gda['name'] = gda['name'].str.lower()

    #prepare xlsx file
    init_xlsx = pd.read_excel(xlsx, sheet_name=None)
    localities = init_xlsx['Sheet1']
    localities_header = np.char.lower(localities.columns.values.astype(str))
    localities.columns = localities_header
    for category in localities_header:
        localities[category] = localities[category].str.lower()

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

def churning_1(data, output, places):
    for place in places:
        count = 0
        for line in data:
            if place == line[0].strip().lower():
                count += int(line[15])
        output.append([place, count])
    return output

def churning_2(data, output, locality, crimes, years): #for statistical analysis?
    '''crime, year = pd.core.reshape.util.cartesian_product([crimes, years])
    df = pd.DataFrame(dict(l = locality, l1=crime, l2=year, l3 = 0))
    for crime in crimes:
        for year in years:
            output.append([locality, crime, year, 0])
    for out in output:
        for line in data:
            if (out[1] == line[1].strip().lower() and out[2] == line[2].strip().lower()):
                line[3] = line[15]
    return output, df'''
    [output.append([locality, data.loc[i, 'website category names'], data.loc[i, 'year'], data.loc[i, 'annual']]) for i in range(0, data.shape[0]) if locality == data.loc[i, 'suburb']]
    #for i in range(0, data.shape[0]):
    #    if locality == data.loc[i, 'suburb']:
    #        output.append([locality, data.loc[i, 'website category names'], data.loc[i, 'year'], data.loc[i, 'annual']])
    return output

def churning_3(data, output, offence):
    for line in data:
        if offence == line[1].strip().lower():
            output.append([line[0].strip().lower(), offence, line[2].strip().lower(), line[15]])
    return output

def churning_4(data, output, date):
    for line in data:
        if date == line[2].strip().lower():
            output.append([line[0].strip().lower(), line[1].strip().lower(), date, line[15]])
    return output

def churning_5(data, output, locality, offence):
    for line in data:
        if (locality == line[0].strip().lower() and offence == line[1].strip().lower()):
            output.append([locality, offence, line[2].strip().lower(), line[15]])
    return output

def churning_6(data, output, offence, date):
    for line in data:
        if (offence == line[1].strip().lower() and date == line[2].strip().lower()):
            output.append([line[0].strip().lower(), offence, date, line[15]])
    return output

def churning_7(data, output, locality, date):
    for line in data:
        if (locality == line[0].strip().lower() and date == line[2].strip().lower()):
            output.append([locality, line[1].strip().lower(), date, line[15]])
    return output

def churning_8(data, output, locality, offence, date):
    for line in data:
        if (locality == line[0].strip().lower() and offence == line[1].strip().lower() and date == line[2].strip().lower()):
            output.append([locality, offence, date, line[15]])
    return output

#def churning_9(data, output, places, crimes, years, selectors):
    #all,all,all should be the default selectors
    #afterwards should it be every single selector change rerun this function?
    #if so, how to make it a recurring function?
    if (selectors.locality == 'all' and selectors.offence == 'all' and selectors.date == 'all'):
        for place in places:
            count = 0
            for line in data:
                if place == line[0].strip().lower():
                    count += int(line[15])
        output.append([place, count])
    elif (selectors.locality != 'all' and selectors.offence == 'all' and selectors.date == 'all'):
        for crime in crimes:
            for year in years:
                output.append([selectors.locality, crime, year, 0])
        for out in output:
            for line in data:
                if (out[1] == line[1].strip().lower() and out[2] == line[2].strip().lower()):
                    line[3] = line[15]
    elif (selectors.locality == 'all' and selectors.offence != 'all' and selectors.date == 'all'):
        for line in data:
            if offence == line[1].strip().lower():
                output.append([line[0].strip().lower(), offence, line[2].strip().lower(), line[15]])
    elif (selectors.locality == 'all' and selectors.offence == 'all' and selectors.date != 'all'):
        for line in data:
            if date == line[2].strip().lower():
                output.append([line[0].strip().lower(), line[1].strip().lower(), date, line[15]])
    elif (selectors.locality != 'all' and selectors.offence != 'all' and selectors.date == 'all'):
        for line in data:
            if (locality == line[0].strip().lower() and offence == line[1].strip().lower()):
                output.append([locality, offence, line[2].strip().lower(), line[15]])
    elif (selectors.locality == 'all' and selectors.offence != 'all' and selectors.date != 'all'):
        for line in data:
            if (offence == line[1].strip().lower() and date == line[2].strip().lower()):
                output.append([line[0].strip().lower(), offence, date, line[15]])
    elif (selectors.locality != 'all' and selectors.offence == 'all' and selectors.date != 'all'):
        for line in data:
            if (locality == line[0].strip().lower() and date == line[2].strip().lower()):
                output.append([locality, line[1].strip().lower(), date, line[15]])
    elif (selectors.locality != 'all' and selectors.offence != 'all' and selectors.date != 'all'):
        for line in data:
            if (locality == line[0].strip().lower() and offence == line[1].strip().lower() and date == line[2].strip().lower()):
                output.append([locality, offence, date, line[15]])
    #return output

#def churning_10(data, output, places, crimes, years, selectors):
    return output

#Data = 'WA-Crime\Locality Crime Data.xlsx'
datafile = 'Locality_Data_Filtered (from Quart Website Rep Mar213-2.csv'
geojson = r'C:\Users\seanl\myprojects\CITS3200\GDA2020\Localities_LGATE_234_WA_GDA2020_Public.geojson'
xlsx = 'Suburb Locality.xlsx'


def main():
    #beginning two lines prepares/checks the files and creates the selector options
    data, gda, localities = file_prep(datafile, geojson, xlsx)
    places, crimes, dates, months, quarters = selector_options(data)
    #maybe the function just runs through each new iteration of selectors when the selectors are changed on the UI
    selectors, output = data_input()
    if (selectors.locality == 'all' and selectors.offence == 'all' and selectors.date == 'all'):
        result = churning_1(data, output, places)
    elif (selectors.locality != 'all' and selectors.offence == 'all' and selectors.date == 'all'):
        result= churning_2(data, output, selectors.locality, crimes, dates)
    '''elif (selectors.locality == 'all' and selectors.offence != 'all' and selectors.date == 'all'):
        result = churning_3(data, output, selectors.offence)
    elif (selectors.locality == 'all' and selectors.offence == 'all' and selectors.date != 'all'):
        result = churning_4(data, output, selectors.date)
    elif (selectors.locality != 'all' and selectors.offence != 'all' and selectors.date == 'all'):
        result = churning_5(data, output, selectors.locality, selectors.offence)
    elif (selectors.locality == 'all' and selectors.offence != 'all' and selectors.date != 'all'):
        result = churning_6(data, output, selectors.offence, selectors.date)
    elif (selectors.locality != 'all' and selectors.offence == 'all' and selectors.date != 'all'):
        result = churning_7(data, output, selectors.locality, selectors.date)
    elif (selectors.locality != 'all' and selectors.offence != 'all' and selectors.date != 'all'):
        result = churning_8(data, output, selectors.locality, selectors.offence, selectors.date)'''
    print(result[:5])

if __name__ == '__main__':
    main()