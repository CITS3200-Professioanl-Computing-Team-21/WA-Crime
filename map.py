#import folium
#from html2image import Html2Image
#import matplotlib.pyplot as plt
#m = folium.Map(location=[-31.9535132, 115.85704710000005], zoom_start=12)
#m.save('test.html')
#hti = Html2Image()
#hti.screenshot(html_file='test.html', save_as='out.png')

import os
import csv
import numpy as np
import pandas as pd
import geopandas as gpd
import json
#import folium
#import seaborn as sns
import scipy as sp
from scipy import stats
import matplotlib.pyplot as plt
#import boundaries

def check_text(textfile):
    #to check if file exists
    if not os.path.isfile(textfile): 
        return None
    else:
        return True

#def file_prep(datafile, geojson, xlsx_csv, coordinates):
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

def new_file_prep(datafile, xlsx_csv):
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

    #prepare localities file
    localities = pd.read_csv(xlsx_csv)
    localities_header = np.char.lower(localities.columns.values.astype(str))
    localities.columns = localities_header
    for header in localities_header:
        localities[header] = localities[header].str.lower()
    localities = localities.rename(columns = {'sub_txt': 'suburb'})
    return (data, localities)

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

def data_input_extended(query):
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
    #print('The input format is name, locality, year, distribution, offence')
    #v,w,x,y,z = input('{} {} {} {} {}').split(',')
    #selectors = new_selector(v.strip().lower(), w.strip().lower(),x.strip().lower(), y.strip().lower(), z.strip().lower())
    selectors = new_selector(query[0].strip().lower(),query[1].strip().lower(),query[2].strip().lower(),query[3].strip().lower(),query[4].strip().lower())
    #fix selectors.year
    
    if selectors.locality == 'all':
        selectors.name = 'all'
        selectors.locality = 'suburb'

    if selectors.year == 'all' or selectors.year == 'all-all':
        selectors.year = '2010-21'
    elif selectors.year.split('-')[0] == 'all' or selectors.year.split('-')[-1] == 'all':
        temp = selectors.year.split('-')
        temp.remove('all')
        selectors.year = '-'.join(temp)
    elif len(selectors.year.split('-')) == 4:
        selectors.year = selectors.year[:5] + selectors.year[-2:]

    if selectors.distribution == 'all-all':
        selectors.distribution = 'all'
    elif '-' in selectors.distribution:
        if selectors.distribution.split('-')[0] == 'all' or selectors.distribution.split('-')[1] == 'all':
            temp = selectors.distribution.split('-')
            temp.remove('all')
            selectors.distribution = temp
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

    png = png_plots(output, selectors)
    #print(output)

    col_num = np.array(q0) - 3
    [col_list.append(distribution[i]) for i in col_num]
    output['sum'] = output[col_list].sum(axis=1)
    output = output[output.columns[[0, 1, 2, -1]]]
    names_list = output['suburb'].drop_duplicates().sort_values().tolist()
    
    #print(output) 

    if selectors.offence != 'all':
        output = output.loc[output['website category names'] == selectors.offence]
        output = output.rename(columns = {'suburb': 'name'})
    elif selectors.offence == 'all':
        output = output.groupby(['suburb'])['sum'].sum()
        output = pd.DataFrame({'name': names_list, 'sum': list(output)})

    #print(output)

    columns = output['name'].drop_duplicates().sort_values().tolist()
    sums = list(output.groupby(['name'])['sum'].sum())
    result = pd.DataFrame({'name':columns, 'sum':sums})
    result = result.set_index('name').reindex(names_list).reset_index()
    result['sum'] = result['sum'].fillna(0)
    result = result.astype(int, errors='ignore')

    #print(result)
    
    return result, png

def mini_churning(name_list, selectors, sum_list, data, localities, years, distribution):
    for name in name_list:
        selectors.name = name
        temp_result, png = churning_final(data, localities, years, distribution, selectors)
        sum_list.append(temp_result['sum'].sum())
    result = pd.DataFrame({'name': name_list, 'sum': list(sum_list)})
    return result, png

def png_plots(output, selectors):
    #time series analysis
    ##full range of 2010-21, or custom? no standardization tho...
    #plot based on years if single location
    #plot based on months if single year and location
    #plot based on locations if station/district/region
    ##remember to filter out crimes
    col_list = list(output)
    output = output.loc[output['website category names'] == selectors.offence]
    output['sum'] = output[col_list].sum(axis=1)
    #print(output)
    if len(output['suburb'].drop_duplicates().sort_values().tolist()) > 1:
        png, ax = plt.subplots(1, 2, tight_layout =True)
        #plot by locations, screw histograms
        #print(sum_list.T) #for histograms, but screw them
        sum_list = output.groupby(['suburb'])['sum'].sum()
        line_list = output.groupby(['suburb'])[col_list[-4:]].sum()
        names_list = output['suburb'].drop_duplicates().sort_values().tolist()
        ax[0].plot(line_list.T)
        ax[0].legend(list(line_list.T))
        ax[0].set_xlabel('hi')
        ax[1].bar(names_list, sum_list)
        ax[1].set_xticklabels(names_list, rotation=45)
    elif len(output['suburb'].drop_duplicates().sort_values().tolist()) == 1:
        png, ax = plt.subplots()
        if len(output['year'].drop_duplicates().sort_values().tolist()) > 1:
            #plot by year
            sum_list = output.groupby(['year'])['sum'].sum()
        elif len(output['year'].drop_duplicates().sort_values().tolist()) == 1:
            #plot by month
            output = output.drop(output.columns[[0, 1, 2]], axis = 1) 
            sum_list = output.sum(axis=0)
        ax.plot(sum_list)
    #ax[1].xticks(rotation=90)
    #plt.xticks(rotation=90)
    png.savefig('test.png')
    return png

#def useless():
    #if year_range >= 5:
    #    plot based on years
    #elif year_range < 5:
    #    if possible, highlight queried distributions????
    #    plot based on months (up to 59 months)

def statistics(sums):
    #compile into list, eventually into masterclass
    ### t-test and pvalues
    num = len(sums)
    sums = np.array(sums).astype(int)
    mean = np.mean(sums)
    #median = np.median(sums) #maybe useless due to instances of overwhelming 0s
    #mode = stats.mode(sums) #maybe useless
    var = np.var(sums)
    #stddev = np.std(sums)
    #stde = np.std(sums, ddof=1) / np.sqrt(np.size(sums))
    std_dev = stats.tstd(sums) #sqrt(var)
    std_e = stats.sem(sums) #sd/sqrt(n)
    stat = [mean, var, std_dev, std_e]
    #stats.ttest_1samp
    #(calculated mean-sample value)/standard error
    ##observed value being sum_counts, caluclated mean being query/sample mean
    ##sed = (std(population)/sqrt(sample_count))
    #If abs(t-statistic) <= critical value: Accept null hypothesis that the means are equal.
    #If abs(t-statistic) > critical value: Reject the null hypothesis that the means are equal.
    #If p > alpha: Accept null hypothesis that the means are equal.
    #If p <= alpha: Reject null hypothesis that the means are equal.
    return stat

def main(query):
    #to ignore warning [[]], code will run as per normal
    pd.options.mode.chained_assignment = None

    #first section of code prepares/checks the files
    #datafile = 'crime.csv'
    #datafile = 'Locality_Data_Filtered (from Quart Website Rep Mar213-2.csv'
    datafile = 'clean_crime.csv'
    #geojson = r'Localities_LGATE_234_WA_GDA2020_Public.geojson'
    xlsx_csv = 'Suburb Locality.csv'
    #coordinates = 'final_data.json'
    sum_list = []
    if check_text(datafile) == None:
        return None
    #if check_text(geojson) == None:
        return None
    if check_text(xlsx_csv) == None:
        return None
    #if check_text(coordinates) == None:
        return None
    #ignore gda and boundaries for now
    data, localities = new_file_prep(datafile, xlsx_csv)

    #places, crimes, years, months, quarters = selector_options(data)
    places, types, suburb, station, district, region, crimes, years, distribution = selector_options_expanded(data, localities)

    #when preparing the data, collect the queries in the selectors format first
    #after error-checking them, filter from data to get only the required localities
    #after filtering, sum according to distribution and years where necessary
    #after sum, grab coordinates from boundaries to complete the variable

    #step1: filter based on years
    #step2: filter based on distribution
    #step3: filter based on offences
    #step4: sum counts based on name and zone_type

    selectors = data_input_extended(query)

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
            result, png = churning_final(data, localities, years, distribution, selectors)
        elif selectors.locality == 'district':
            name_data = localities.loc[localities[selectors.locality] == selectors.name]
            name_list = name_data['station'].drop_duplicates().sort_values().tolist()
            selectors.locality = 'station'
            result, png = mini_churning(name_list, selectors, sum_list, data, localities, years, distribution)
        elif selectors.locality == 'region':
            name_data = localities.loc[localities[selectors.locality] == selectors.name]
            name_list = name_data['district'].drop_duplicates().sort_values().tolist()
            selectors.locality = 'district'
            result, png = mini_churning(name_list, selectors, sum_list, data, localities, years, distribution)
    elif selectors.name == 'all':
        name_list = locals()[selectors.locality]
        name_list.remove('unknown')
        name_list.remove('all')
        result, png = mini_churning(name_list, selectors, sum_list, data, localities, years, distribution)

    plt.show()
    stat = statistics(result['sum'].sort_values().tolist())
    #print(stat)
    return result, stat, png

    #return ****.html, statistical_info

query1 = ['mandurah', 'station', '2011-18', 'sep-dec', 'robbery']
main(query1)
#query2 = ['mandurah', 'suburb', '2011-18', 'sep-dec', 'robbery']
#main(query2)
#query3 = ['mandurah', 'suburb', '2015-16', 'sep-dec', 'robbery']
#main(query3)
#query4 = ['mandurah', 'station', '2015-16', 'sep-dec', 'robbery']
#main(query4)
#query5 = ['mandurah', 'station', 'all', 'all', 'all']
#main(query5)


#query2 = ['Rockingham', 'Station', '2018-19', 'Q1', 'Arson']
#main(query2)
#query3 = ['all', 'all', 'all-2018-19', 'all', 'all']
#main(query3)
#query4 = ['all', 'all', '2010-11-2015-16', 'all', 'all']
#main(query4)
#if __name__ == '__main__':
 #   main()

#signature [name, zone_type, year_range, distribution, crime]