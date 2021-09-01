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
#import seaborn as sns
#import scipy as sp
#import matplotlib.pyplot as plt


def file_prep(filename):
    with open(filename, 'r') as file:
        data = list(csv.reader(file, delimiter = ','))
        data = data[1:]

    for line in data:
        for i in range(0,len(line)):
            if line[i] == '':
                line[i] = '0'
    return data

def selector_options(data):
    places = []
    crimes = []
    #Jan, Feb, Mar, Apr, May, Jun, Jul, Aug, Sep, Oct, Nov, Dec
    #Jul, Aug, Sep, Oct, Nov, Dec, Jan, Feb, Mar, Apr, May, Jun
    months = [[],[],[],[],[],[],[],[],[],[],[],[]]
    #with months, 2d arrays?
    #if add days, 3d arrays?
    years = []

    #making a list of places
    #State: Western Australia 
    #Region: Metropolitan, Regional
    #District: Armadale, Cannington, Fremantle, Joondalup, Mandurah, Midland, District, Mirrabooka,  Perth, Goldfields-Esperance, Great Southern, 
    #           Kimberley, Mid West-Gascoyne, Pilbara, South West, Wheatbelt
    #Surburbs: ???
    for line in data:
        if line[0] not in places:
            places.append(line[0])
    places = [place.lower() for place in places]
    
    #making a list for the crimes occurred
    for line in data:
        if line[1] not in crimes:
            crimes.append(line[1]) 
    crimes = [crime.lower() for crime in crimes]

    #making a list of all the dates
    for line in data:
        if line[2] not in years:
            years.append(line[2])
    years = sorted(years)
    
    return places, crimes, years

def data_input():
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
    
#def churning_2_temp(data, output, locality):
    count = 0
    for line in data:
        if place == line[0].strip().lower():
            count += int(line[15])
    output.append([place, count])
    return output

def churning_2(data, output, locality, crimes, years): #for statistical analysis?
    for crime in crimes:
        for year in years:
            output.append([locality, crime, year, 0])
    for out in output:
        for line in data:
            if (out[1] == line[1].strip().lower() and out[2] == line[2].strip().lower()):
                line[3] = line[15]
    return output

#def churning_3(data, output, crime):
    count = 0
    for line in data:
        if crime == line[1].strip().lower():
            count += int(line[15])
    output.append([crime, count])
    return output

def churning_3(data, output, offence):
    for line in data:
        if offence == line[1].strip().lower():
            output.append([line[0].strip().lower(), offence, line[2].strip().lower(), line[15]])
    return output

#def churning_4(data, output, date):
    count = 0
    for line in data:
        if date == line[2].strip().lower():
            count += int(line[15])
    output.append([date, count])
    return output

def churning_4(data, output, date):
    for line in data:
        if date == line[2].strip().lower():
            output.append([line[0].strip().lower(), line[1].strip().lower(), date, line[15]])
    return output

#def churning_5(data, output, place, crime):
    count = 0
    for line in data:
        if (place == line[0].strip().lower() and crime == line[1].strip().lower()):
            count += int(line[15])
    output.append([place, crime, count])
    return output

def churning_5(data, output, locality, offence):
    for line in data:
        if (locality == line[0].strip().lower() and offence == line[1].strip().lower()):
            output.append([locality, offence, line[2].strip().lower(), line[15]])
    return output

#def churning_6(data, output, crime, date):
    count = 0
    for line in data:
        if (crime == line[1].strip().lower() and date == line[2].strip().lower()):
            count += int(line[15])
    output.append([crime, date, count])
    return output

def churning_6(data, output, offence, date):
    for line in data:
        if (offence == line[1].strip().lower() and date == line[2].strip().lower()):
            output.append([line[0].strip().lower(), offence, date, line[15]])
    return output

#def churning_7(data, output, place, date):
    count = 0
    for line in data:
        if (place == line[0].strip().lower() and date == line[2].strip().lower()):
            count += int(line[15])
    output.append([place, date, count])
    return output

def churning_7(data, output, locality, date):
    for line in data:
        if (locality == line[0].strip().lower() and date == line[2].strip().lower()):
            output.append([locality, line[1].strip().lower(), date, line[15]])
    return output

#def churning_8(data, output, place, crime, date):
    count = 0
    for line in data:
        if (place == line[0].strip().lower() and crime == line[1].strip().lower() and date == line[2].strip().lower()):
            count += int(line[15])
    output.append([place, crime, date, count])
    return output

def churning_8(data, output, locality, offence, date):
    for line in data:
        if (locality == line[0].strip().lower() and offence == line[1].strip().lower() and date == line[2].strip().lower()):
            output.append([locality, offence, date, line[15]])
    return output

#Data = 'WA-Crime\Locality Crime Data.xlsx'
filename = 'Locality_Data_Filtered (from Quart Website Rep Mar213-2.csv'

def main():
    data = file_prep(filename)
    places, crimes, dates = selector_options(data)
    selectors, output = data_input()
    if (selectors.locality == 'all' and selectors.offence == 'all' and selectors.date == 'all'):
        result = churning_1(data, output, places)
    elif (selectors.locality != 'all' and selectors.offence == 'all' and selectors.date == 'all'):
        result = churning_2(data, output, selectors.locality, crimes, dates)
    elif (selectors.locality == 'all' and selectors.offence != 'all' and selectors.date == 'all'):
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
        result = churning_8(data, output, selectors.locality, selectors.offence, selectors.date)
    df = pd.DataFrame(result)
    final = df.sort_values(by=1)
    print(final.head(5))
    print(final.shape)

if __name__ == '__main__':
    main()