import csv, sqlite3, os, pandas
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy import stats

# Desktop (windows) works for relative addresses for some reason, Mac doesn't
# Desktop location: C:/Users/User/OneDrive/Uni/CITS3200/WA-Crime/data.db
# Mac location /Users/blank/OneDrive/Uni/CITS3200/WA-Crime/data.db

def filter(name, zone, year, mq, offence):

    # Stupid inconsistency between files
    year = year.lower()
    if mq == 'All':
        mq = mq.lower()
    elif mq[0] == "-":
        mq = mq[1:]
    offence = offence.lower()
    name = name.lower()
    database = "data.db"
    crime_file = "crime.csv"
    localities_file = "localities.csv"

    # Year_fn is financial year starting year. Do not need to store the
    # following year - it is implied. Use of integer makes for easier
    # comparison.
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS Crime (
                                        suburb text NOT NULL,
                                        crime text NOT NULL,
                                        year_fn int NOT NULL,
                                        jul int,
                                        aug int,
                                        sep int,
                                        oct int,
                                        nov int,
                                        dec int,
                                        jan int,
                                        feb int,
                                        mar int,
                                        apr int,
                                        may int,
                                        jun int,
                                        annual int
                                    ); """

    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS Localities (
                                    suburb text PRIMARY KEY NOT NULL,
                                    station text NOT NULL,
                                    district text NOT NULL,
                                    region text NOT NULL
                                );"""

    # Create a database connection
    conn = create_connection(database)

    # Create tables if they don't exist, create cursor
    if conn is not None:
        c = conn.cursor()
        # Create data table
        filled = create_table(c, sql_create_projects_table, "Crime")
        # Only fill tables if no data in them - avoids redundantly doing
        # it each time.
        if not filled:
            fill_table(c, crime_file, "Crime")
        conn.commit()

        # Create localities table
        filled = create_table(c, sql_create_tasks_table, "Localities")
        if not filled:
            fill_table(c, localities_file, "Localities")
        conn.commit()
    else:
        print("Error! cannot create the database connection.")
        return
    
    # Build query in stages
    query0 = ""
    query1 = ""
    mrange = ""
    y1, y2 = 0, 0
    
    print(mq)

    if str(mq).find('all') == -1:
        # If it is a single month entry, i.e. no - found, mrange is just that one month
        mrange = str(distribution(mq))
    else:
        # We assume no more updates to the calendar system
        mq = "jul-jun"
        mrange = str(distribution(mq))

    # If there is an 'all' type input assume all year range.
    # print(year)
    if str(year).find('all') == -1:
        y1, y2 = yrange(year)
    else:
        # In-built Y3K bug
        y1, y2 = "0", "3000"
    # If year order came in the wrong way
    if y1 > y2:
        y2, y1 = y1, y2
    # query += "SELECT " + zone + ", " + mrange + " AS Total FROM Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb"
    # query += "SELECT Crime." + zone + ", " + mrange + " AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb) WHERE Crime.Suburb = '" + name + "'"
    
    # Determines subordinate zone type for selection and grouping (This feature may be made redundant in the future in favour of a custom zone selection)
    zones = ['suburb', 'station', 'district', 'region']
    sub_zone = ""

    # All selection for zone defaults to suburb, also resets sub_zone and name to 'all' so that all suburbs are selected.
    if zone == 'all' or zone == 'suburb':
        zone = 'suburb'
        sub_zone = 'suburb'
        name = 'all'

    # When name is 'all', we return all of that zone type, therefore no subzones. When name is not all, we return only the named zone and it's subzones.
    if name != 'all':
        sub_zone = zones[zones.index(zone) - 1]
    else:
        sub_zone = zone

    # Below is for a more descriptive query result
    # query += "SELECT Localities." + sub_zone + ", " + "Crime, Year_fn, Localities." + zone + ", SUM(" + mrange + ") AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb)"

    print(y1, y2, sub_zone, zone, mrange, offence, name)

    allmonth = "jul + aug + sep + oct + nov + dec + jan + feb + mar + apr + may + jun"

    # We only show every month if we have a narrow year search less than 4 years, otherwise show overall year trends
    query0 += "CREATE TEMPORARY TABLE unfiltered AS SELECT Localities." + sub_zone + ", year_fn, jul, aug, sep, oct, nov, dec, jan, feb, mar, apr, may, jun, " + allmonth + " FROM (Crime LEFT OUTER JOIN Localities ON Crime.suburb = Localities.suburb)"
    # CURRENT PROBLEM. LEAKS AROUND YEAR_FN REQUIRING YOU INCLUDE PREVIOUS OR FOLLOWING YEARS
    if name != 'all' or offence != 'all' or year != 'all':
        query0 += " WHERE"
        # includeand to check if query has multiple conditions, so that "AND" can be appended to include them
        includeand = False
        if name != 'all':
            query0 += " Localities." + zone + " = '" + name.lower() + "'"
            includeand = True
        if offence != 'all':
            if includeand:
                query0 += " AND"
            query0 += " Crime = '" + offence.lower() + "'"
            includeand = True
        if year != 'all':
            if includeand:
                query0 += " AND"
            query0 += " year_fn >= " + y1 + " AND year_fn < " + y2
    # if int(y2) - int(y1) > 4:
    #     query0 += " GROUP BY year_fn, Localities." + sub_zone + " ORDER BY Localities." + sub_zone
    # if sub_zone == 'Suburb':
    #     query += " GROUP BY Year_fn, Localities." + sub_zone + " ORDER BY Localities." + sub_zone
    # else:
    #     query += " GROUP BY Year_fn, " + sub_zone + " ORDER BY " + sub_zone

    # # Don't group by year
    # if sub_zone == 'suburb':
    #     query += " GROUP BY Localities." + sub_zone + " ORDER BY Localities." + sub_zone
    # else:
    #     query += " GROUP BY " + sub_zone + " ORDER BY " + sub_zone

    # OLD CODE OLD CODE
    # query += "SELECT Localities." + sub_zone + ", SUM(" + mrange + ") AS total FROM (Crime LEFT OUTER JOIN Localities ON Crime.suburb = Localities.suburb)"
    # # CURRENT PROBLEM. LEAKS AROUND YEAR_FN REQUIRING YOU INCLUDE PREVIOUS OR FOLLOWING YEARS
    # if name != 'all' or offence != 'all' or year != 'all':
    #     query += " WHERE"
    #     # includeand to check if query has multiple conditions, so that "AND" can be appended to include them
    #     includeand = False
    #     if name != 'all':
    #         query += " Localities." + zone + " = '" + name.lower() + "'"
    #         includeand = True
    #     if offence != 'all':
    #         if includeand:
    #             query += " AND"
    #         query += " Crime = '" + offence.lower() + "'"
    #         includeand = True
    #     if year != 'all':
    #         if includeand:
    #             query += " AND"
    #         query += " year_fn >= " + y1 + " AND year_fn < " + y2
    # # if sub_zone == 'Suburb':
    # #     query += " GROUP BY Year_fn, Localities." + sub_zone + " ORDER BY Localities." + sub_zone
    # # else:
    # #     query += " GROUP BY Year_fn, " + sub_zone + " ORDER BY " + sub_zone

    # # Don't group by year
    # if sub_zone == 'suburb':
    #     query += " GROUP BY Localities." + sub_zone + " ORDER BY Localities." + sub_zone
    # else:
    #     query += " GROUP BY " + sub_zone + " ORDER BY " + sub_zone

    # # All crime type all year type
    # query += "SELECT Localities." + sub_zone + ", " + "Crime, Year_fn, Localities." + zone + ", SUM(" + mrange + ") AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb)"
    # # CURRENT PROBLEM. YEAR_FN IS ISNT PROPERLY INT FORM, CANT DO COMPARISON 
    # query += " WHERE Localities." + zone + " = '" + name.lower() + "'"
    # query += " GROUP BY Year_fn, " + sub_zone + " ORDER BY " + sub_zone

    # conn.commit()

    print(query0) #unfiltered query
    
    # Print output to command line
    c.execute(query0)
    
    # Select from temp table
    c.execute("SELECT * FROM unfiltered")
    j = 0
    unfiltered = []
    for i in c.fetchall():
        unfiltered.append(list(i))
        # print(j, i)
        j += 1
    # print(c.fetchall())

    # print(query)
    unfiltered = convert(unfiltered, ["name", "year_fn", "jul", "aug", "sep", "oct", "nov", "dec", "jan", "feb", "mar", "apr", "may", "jun", "total"])
    # unfiltered = convert(unfiltered, ["name", "year_fn", "total"])
    # print(unfiltered)
    # return unfiltered

    # Following is to apply final filters to data
    if mrange != allmonth:
        query1 += "SELECT " + sub_zone + ", SUM(" + mrange + ") AS total FROM unfiltered"
    else:
        query1 += "SELECT " + sub_zone + ", total FROM unfiltered"
    query1 += " GROUP BY " + sub_zone + " ORDER BY " + sub_zone
    print(query1) #filtered query
    c.execute(query1)
    j = 0
    filtered = []
    for i in c.fetchall():
        filtered.append(list(i))
        # print(j, i)
        j += 1
    filtered = convert(filtered, ["name", "sum"])

    graphs = []
    anomalies = [] #empty for now
    anomalies = convert(anomalies, ["name", "stat"])
    # graphs, anomalies = statistics(unfiltered)
    # return filtered, graphs, anomalies
    #graphs, anomalies = statistics(filtered, unfiltered)
    fig, anomalies = statistics(filtered, unfiltered, mrange)
    
    print('it works')
    plt.savefig('test.png')
    plt.show()

    if anomalies == []:
        anomalies = 'CHOOSE BETTER QUERY' #CHANGE THIS PLEASE

    print(anomalies)
    return filtered, plt.figure(1), anomalies

def statistics(filtered, unfiltered, mrange):
    #think of more meaningful labelling methods if possible
    #add x and y labels
    name_list = unfiltered['name'].drop_duplicates().sort_values().tolist()
    year_list = unfiltered['year_fn'].drop_duplicates().sort_values().tolist()
    temp1 = unfiltered[unfiltered.columns[[0,1]]]
    if '+' not in mrange:
        temp2 = unfiltered[mrange]
    elif '+' in mrange:
        temp2 = unfiltered[mrange[1:-1].split('+')]
    dataframe = pandas.concat([temp1, temp2], axis=1)
    if len(year_list) > 5:
        for i in range(len(name_list)):
            values = unfiltered.loc[unfiltered['name'] == name_list[i]]
            extracted_values = values[values.columns[-1:]].values.tolist()
            plot_values = []
            for i in extracted_values:
                plot_values += i
            plt.plot(year_list, plot_values)
        plt.legend(name_list)
        plt.xticks(rotation=45)
    elif len(year_list) <= 5:
        #if possible, highlight queried distributions????
        #plot based on months (up to 60 months)
        for i in range(len(name_list)):
            values = dataframe.loc[dataframe['name'] == name_list[i]]
            extracted_values = values[values.columns[2:]].values.tolist()
            plot_values = []
            for i in extracted_values:
                plot_values += i
            months = []
            for i in range(len(year_list)):
                months += values[values.columns[2:]].columns.tolist()
            print(extracted_values)
            print(months)
            count = 0
            for i in year_list:
                for j in range(len(values[values.columns[2:]].columns.tolist())):
                    months[count] += str(i)[2:]
                    count += 1
            plt.plot(months, plot_values)
        plt.legend(name_list)
        plt.xticks(rotation=45)

    #plt.show()

    temp = []
    anomalies = []
    if len(year_list) > 1:
        for a in range(len(name_list)):
            values = dataframe.loc[dataframe['name'] == name_list[a]]
            extracted_values = values[values.columns[2:]].values.tolist()
            plot_values = []
            for i in extracted_values:
                plot_values += i
            months = []
            for i in range(len(year_list)):
                months += values[values.columns[2:]].columns.tolist()
            count = 0
            for i in year_list:
                for j in range(len(values[values.columns[2:]].columns.tolist())):
                    months[count] += str(i)[2:]
                    count += 1
            nums = len(plot_values)
            mean = np.mean(plot_values)
            count = 0
            for k in extracted_values:
                std_e = stats.sem(k)
                result = stats.ttest_1samp(k, mean)
                temp.append([name_list[a], year_list[count], mean, std_e, result.pvalue])
                count += 1
        for i in temp:
            if i[-1] < 0.05:
                anomalies.append(i)
    elif len(year_list) <= 1:
        for a in range(len(name_list)):
            t_value = []
            p_value = []
            #are we comparing against rest of the year, or specifically this sample size?
            values = dataframe.loc[dataframe['name'] == name_list[a]]
            extracted_values = values[values.columns[2:]].values.tolist()
            month_list = values[values.columns[2:]].columns.tolist()
            plot_values = []
            for i in extracted_values:
                plot_values += i
            num = len(plot_values)
            print(plot_values)
            mean = np.mean(plot_values)
            std_e = stats.sem(plot_values)
            for i in plot_values:
                t_value.append((i-mean)/(std_e))
            for i in t_value:
                p_value.append(stats.t.sf(i, df = (num -1)))
            count = 0
            for i in p_value:
                if i < 0.05:
                    anomalies.append([name_list[a], month_list[count], mean, std_e, i])
                count += 1

    #stats.ttest_1samp
    #(calculated mean-sample value)/standard error
    ##observed value being sum_counts, caluclated mean being query/sample mean
    ##sed = (std(population)/sqrt(sample_count))
    #If abs(t-statistic) <= critical value: Accept null hypothesis that the means are equal.
    #If abs(t-statistic) > critical value: Reject the null hypothesis that the means are equal.
    #If p > alpha: Accept null hypothesis that the means are equal.
    #If p <= alpha: Reject null hypothesis that the means are equal.

    return plt.figure(1), anomalies

def distribution(mq):
    # Collects the months whose data are to be summed, scans from m0 to m1 collecting
    # months in between.
    months = ["jul", "aug", "sep", "oct", "nov", "dec", "jan", "feb", "mar", "apr", "may", "jun"]
    query = ""
    if mq != 'all':
        # Quarters not done yet
        mrange = "("
        # if mq[0] == 'q':
        #     if str(mq).find("-") != -1:
        #         mq = mq.split("-")

        mq = str(mq).split("-")

        # Check if it is a range, meaning split by - was successful
        if len(mq) > 1:

            if mq[0][0] == 'q':
                # Calculate starting month
                mq[0] = months[(int(mq[0][1])-1)*3]
                mq[1] = months[(int(mq[1][1]))*3-1]

            m0 = mq[0]
            m1 = mq[1]
            mi = months.index(m0)
            curr = m0
            while curr != m1:
                mrange += curr + "+"
                # If Sep-Aug we modulo past Dec until we reach Aug
                mi = (mi + 1) % 12
                curr = months[mi]
            # Closes the range with bracket
            mrange += curr + ')'
            # print(mrange)
            return mrange
        else:
            # Assuming no months will ever start with Q
            if mq[0][0] == 'q':
                # Calculate starting month
                start = months[(int(mq[0][1])-1)*3]
                mi = months.index(start)
                end = months[int(mq[0][1])*3-1]
                while start != end:
                    mrange += start + "+"
                    # If Sep-Aug we modulo past Dec until we reach Aug
                    mi = (mi + 1) % 12
                    start = months[mi]
                mrange += start + ')'
                return mrange
            else:
                return mq[0]
            

        # m0 = mq[0:3]
        # # Index of first month so we can iterate through list
        # mi = months.index(m0)
        # m1 = mq[4:]
        # curr = m0


# May be buggy for weird inputs like 'all-2013-2014' or '2013-2014-all' or 'all-all'
def yrange(year):
    y = year.split('-')
    # print(y)
    # Stupid selector input difference has me doing this stupidness. Format for end year 2021 is '21', so I need to infer the century and add 21 to it to get the year I want '2021'
    return y[0], str(int(int(y[-2])/100)) + y[-1]

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except:
        print("Connect to database error") 
    return conn

def create_table(c, create_table_sql, table):
    try:
        # Only create table if it doesn't exist (data can't be accessed)
        try:
            # LIMIT 1 just to make the selection quick if table does exist.
            query = "SELECT * FROM " + table + " LIMIT 1"
            c.execute(query)
            # Return true to indicate table exists and has data, no need to fill it again.
            # print(c.rowcount)
            if len(c.fetchall()) > 0:
                return True
            return False
        except:
            c.execute(create_table_sql)
            return False
    except:
        print("Create table error")
        return None

# This shit isn't working for some reason. NOW IT IS
def fill_table(c, file_name, table):
    try:
        with open(file_name, 'r') as f:
            reader = csv.reader(f)
            columns = next(reader)
            query = "INSERT INTO " + table + " VALUES({})".format(','.join('?' * len(columns)))
            for data in reader:
                # Also converts everything to lower case
                data = [e.lower() for e in data]
                # Turn year_fn into an int that is just the beginning year. 
                if table == "Crime":
                    data[2] = int(data[2].split("-")[0])
                c.execute(query, data)
            c.commit()
    except:
        print("Error filling table data")
    
# Converts list to pandas data frame    
def convert(list, cols):
    df = pandas.DataFrame(list, columns = cols)
    print(df)
    return df


# Name, zone, year, month/quarter, crime
filter('perth', 'station', '2015-16-2019-20', 'jul-oct', 'stealing') # <5 years
filter('perth', 'station', '2014-15-2019-20', 'jul-oct', 'stealing') # >5 years
filter('perth', 'station', '2014-15', 'jul-oct', 'stealing') # 1 year
filter('perth', 'station', '2014-15', 'jul', 'stealing') #1 year, 1 month
filter('perth', 'station', '2014-15-2019-20', 'jul', 'stealing') # <5years, 1 month, fix
filter('perth', 'station', '2015-16-2019-20', 'jul', 'stealing') # >5years, 1 month, fix

#perth district = 92571, wembley station = 34120



