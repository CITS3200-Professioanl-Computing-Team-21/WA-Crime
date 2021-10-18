import csv, sqlite3, os, pandas
from operator import sub
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
from scipy import stats

def filter(name, zone, year, mq, offence):

    # Make sure all inputs are lower case
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

    # Construct month range for query. If 'all', defaults to jul-jun
    if str(mq).find('all') == -1:
        mrange = str(distribution(mq))
    else:
        # We assume no more updates to the calendar system
        mq = "jul-jun"
        mrange = str(distribution(mq))

    # Construct year range for query. If 'all', defaults to max year range
    if str(year).find('all') == -1:
        y1, y2 = yrange(year)
    else:
        # In-built Y3K bug
        y1, y2 = "0", "3000"
    # If year order came in the wrong way
    if y1 > y2:
        y2, y1 = y1, y2
    
    # Determines subordinate zone type for selection and grouping
    zones = ['suburb', 'station', 'district', 'region']
    sub_zone = ""

    # When name is 'all', we return all of that zone type, therefore no subzones. When name is not all, we return only the named zone and it's subzones. 
    # If zone is suburb and named, we return the station that named suburb belongs to.
    if name != 'all':
        if zone == 'suburb':
            sub_zone = 'suburb'
            zone = 'station'
            get_station = "SELECT station FROM Localities WHERE suburb = '" + name + "'"
            c.execute(get_station)
            name = c.fetchone()[0]
        else:
            sub_zone = zones[zones.index(zone) - 1]
    else:
        sub_zone = zone

    # Sum across every month for 'total' column, used for unfiltered data
    allmonth = "SUM(jul) + SUM(aug) + SUM(sep) + SUM(oct) + SUM(nov) + SUM(dec) + SUM(jan) + SUM(feb) + SUM(mar) + SUM(apr) + SUM(may) + SUM(jun)"

    # Default unfiltered data query
    query0 += "CREATE TEMPORARY TABLE unfiltered AS SELECT Localities." + sub_zone + ", year_fn, SUM(jul) as jul, SUM(aug) as aug, SUM(sep) as sep, SUM(oct) as oct, SUM(nov) as nov, SUM(dec) as dec, SUM(jan) as jan, SUM(feb) as feb, SUM(mar) as mar, SUM(apr) as apr, SUM(may) as may, SUM(jun) as jun, " + allmonth + " as total FROM (Crime LEFT OUTER JOIN Localities ON Crime.suburb = Localities.suburb)"

    # Construction of unfiltered data query
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
    query0 += " GROUP BY Localities." + sub_zone + ", year_fn"
    
    # Run query to make temp unfiltered table, then get unfiltered data. 
    c.execute(query0)
    c.execute("SELECT * FROM unfiltered")
    j = 0
    unfiltered = []
    for i in c.fetchall():
        unfiltered.append(list(i))
        j += 1
    # Convert to pandas frame
    unfiltered = convert(unfiltered, ["name", "year_fn", "jul", "aug", "sep", "oct", "nov", "dec", "jan", "feb", "mar", "apr", "may", "jun", "total"])

    # Following is to apply final filters to data
    if mrange != allmonth:
        query1 += "SELECT " + sub_zone + ", SUM(" + mrange + ") AS total FROM unfiltered"
    else:
        query1 += "SELECT " + sub_zone + ", total FROM unfiltered"
    query1 += " GROUP BY " + sub_zone + " ORDER BY " + sub_zone
    c.execute(query1)
    j = 0
    filtered = []
    for i in c.fetchall():
        filtered.append(list(i))
        j += 1
    filtered = convert(filtered, ["name", "sum"])


    # Calculate data anomalies
    anomalies = statistics(filtered, unfiltered, mrange)

    # Build data object that holds textual anomaly information, and graph information
    data = statobject(anomalies, offence, unfiltered, mrange)

    # Convert to pandas frame to be used in UI
    if anomalies != []:
        anomalies = convert(anomalies, ["name", "year", "mean", "std_e", "observation", "p-value"])

    # Returns the filtered data to make heatmap, anomaly information, and data object holding textual anomaly information and graph
    return filtered, anomalies, data

# Function for calculating anomalies
def statistics(filtered, unfiltered, mrange):
    name_list = unfiltered['name'].drop_duplicates().sort_values().tolist()
    year_list = unfiltered['year_fn'].drop_duplicates().sort_values().tolist()
    temp1 = unfiltered[unfiltered.columns[[0,1]]]
    if '+' not in mrange:
        temp2 = unfiltered[mrange]
    elif '+' in mrange:
        temp2 = unfiltered[mrange[1:-1].split('+')]
    dataframe = pandas.concat([temp1, temp2], axis=1)
    temp = []
    anomalies = []

    # Anomalies are calculated across years when multiple year range is given
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

            total = []

            for i in range(len(extracted_values)):
                extracted_values[i] = [k for k in extracted_values[i] if k != '']

            for k in extracted_values:
                total.append(sum(k))
            mean = np.mean(total)
            # If total less than or equal to 1, then no std_d can be calculated, so skip
            if len(total) <= 1:
                continue
            std_d = stats.tstd(total)
            # If no std_d, can't determine p value, so skip
            if std_d == 0.0:
                continue
            # Where k is an array that represents the sample
            count = 0
            for k in extracted_values:
                z_value = (sum(k)-mean)/(std_d)
                p_value = stats.norm.sf(abs(z_value))
                temp.append([name_list[a], year_list[count], mean, std_d, sum(k), p_value])
                count += 1  
        for i in temp:
            if i[-1] < 0.05:
                anomalies.append(i)

    # Singular years calculate anomalies based on month range
    elif len(year_list) <= 1:
        for a in range(len(name_list)):
            z_value = []
            p_value = []
            values = dataframe.loc[dataframe['name'] == name_list[a]]
            extracted_values = values[values.columns[2:]].values.tolist()
            month_list = values[values.columns[2:]].columns.tolist()
            plot_values = []
            for i in extracted_values:
                plot_values += i
            num = len(plot_values)
            if num <= 1:
                continue
            mean = np.mean(plot_values)
            std_d = stats.tstd(plot_values)
            if std_d == 0.0:
                continue
            for i in plot_values:
                z_value.append((i-mean)/(std_d))
            for i in z_value:
                p_value.append(stats.norm.sf(abs(i)))
            count = 0
            for i, k in enumerate(p_value):
                if k < 0.05:
                    anomalies.append([name_list[a], month_list[count], mean, std_d, extracted_values[0][i], k])
                count += 1
    
    return anomalies

#Collects the months whose data are to be summed, scans from m0 to m1 collecting months in between.
def distribution(mq):
    months = ["jul", "aug", "sep", "oct", "nov", "dec", "jan", "feb", "mar", "apr", "may", "jun"]
    query = ""
    if mq != 'all':
        mrange = "("

        mq = str(mq).split("-")

        # Check if it is a range, meaning split by - was successful
        if len(mq) > 1:

            if mq[0][0] == 'q':
                # Calculate starting month
                mq[0] = months[(int(mq[0][1])-1)*3]
                mq[1] = months[(int(mq[1][1]))*3-1]

            m0 = mq[0]
            m1 = mq[1]

            # If input query had months out of order, fix
            if months.index(m0) > months.index(m1):
                temp = m1
                m1 = m0
                m0 = temp

            mi = months.index(m0)
            curr = m0
            while curr != m1:
                mrange += curr + "+"
                mi = (mi + 1) % 12
                curr = months[mi]
            # Closes the range with bracket
            mrange += curr + ')'
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
                    mi = (mi + 1) % 12
                    start = months[mi]
                mrange += start + ')'
                return mrange
            else:
                return mq[0]

def yrange(year):
    y = year.split('-')
    # Formatting required to determine the ending year
    return y[0], str(int(int(y[-2])/100)) + y[-1]

# Create database connection
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
            if len(c.fetchall()) > 0:
                return True
            return False
        except:
            c.execute(create_table_sql)
            return False
    except:
        print("Create table error")
        return None

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
    return df

# Data object to hold information returned to application
class statobject:
    def __init__(self, anomalydata, offence, unfiltered, mrange):
        # Text to be displayed in panel 1 summarised anomalies.
        self.anomalies_text = ""
        self.unfiltered = unfiltered
        self.mrange = mrange
        if anomalydata != []:
            self.anomalies_text = text(anomalydata, offence)
    def getGraph(self):
        graph(self.unfiltered, self.mrange)
    def getText(self):
        return self.anomalies_text

# Function to draw time series or bar charts for query
def graph(unfiltered, mrange):
    year_list = unfiltered['year_fn'].drop_duplicates().sort_values().tolist()
    temp1 = unfiltered[unfiltered.columns[[0,1]]]
    if '+' not in mrange:
        temp2 = unfiltered[mrange]
    elif '+' in mrange:
        temp2 = unfiltered[mrange[1:-1].split('+')]
    dataframe = pandas.concat([temp1, temp2], axis=1)

    sorted = unfiltered.sort_values(by=['total'], ascending=False)
    name_list = sorted['name'].drop_duplicates().tolist()
    bar_names = unfiltered['name'].drop_duplicates().tolist()

    # If more than 5 years, we plot years along time series
    if len(year_list) > 5:
        limit = 5
        if len(name_list) < limit:
            limit = len(name_list)
        for i in range(limit):
            values = unfiltered.loc[unfiltered['name'] == name_list[i]]
            data_years = values[values.columns[1]].values.tolist()
            if len(data_years) != len(year_list):
                # i -= 1 
                continue
            extracted_values = values[values.columns[-1:]].values.tolist()
            plot_values = []
            for i in extracted_values:
                plot_values += i
            plt.plot(data_years, plot_values, marker='o')
        plt.legend(name_list)
        plt.xticks(rotation=45)
        plt.xlabel('Years/Months Distribution')
        plt.ylabel('Crime Counts')
    # Less than or equal to 5 years we plot months over those years
    elif len(year_list) <= 5:

        # If a singular month and only one year featured, plot bar graph instead
        if '+' not in mrange and len(year_list) <= 1:
            temp = dataframe.groupby('name')[mrange].sum()
            plt.bar(bar_names, list(temp))
            plt.xticks(rotation=45)
            plt.xlabel('Locations')
            plt.ylabel('Crime Counts')
            plt.title(mrange + str(year_list)[3:-1])
        else:
            limit = 5
            if len(name_list) < limit:
                limit = len(name_list)
            for i in range(limit):
                values = dataframe.loc[dataframe['name'] == name_list[i]]
                extracted_values = values[values.columns[2:]].values.tolist()
                data_years = values[values.columns[1]].values.tolist()
                if len(data_years) != len(year_list):
                    continue
                plot_values = []
                for i in extracted_values:
                    plot_values += i
                months = []
                for i in range(len(data_years)):
                    months += values[values.columns[2:]].columns.tolist()
                count = 0
                for i in data_years:
                    for j in range(len(values[values.columns[2:]].columns.tolist())):
                        months[count] += str(i)[2:]
                        count += 1
                plt.plot(months, plot_values, marker='o')
            plt.legend(name_list)
            plt.xticks(rotation=45)
            plt.xlabel('Years/Months Distribution')
            plt.ylabel('Crime Counts')

    plt.show()

# Generates textual information for anomalies
def text(anomalydata, offence):
    if offence == "all":
        offence = "crime"
    text = ""

    text += "ORDERED BY LOCATION:\n\n"
    for i in range(len(anomalydata)):
        period, name, change = str(anomalydata[i][1]), anomalydata[i][0], "higher" if anomalydata[i][4] > anomalydata[i][2] else "lower"
        percent = abs(anomalydata[i][4]-anomalydata[i][2])/anomalydata[i][2]
        text += name + " (" + period + ")" " had " + str(round(percent*100, 2)) + "% " + change + " " + offence + " than average\n\n"
    
    anomalydata.sort(key=year, reverse=True)
    text += "\n\nORDERED BY DATE:\n\n"

    for i in range(len(anomalydata)):
        period, name, change = str(anomalydata[i][1]), anomalydata[i][0], "higher" if anomalydata[i][4] > anomalydata[i][2] else "lower"
        percent = abs(anomalydata[i][4]-anomalydata[i][2])/anomalydata[i][2]
        text += name + " (" + period + ")" " had " + str(round(percent*100, 2)) + "% " + change + " " + offence + " than average\n\n"

    return text

# Sorting method for dates
def year(anom):
    if type(anom[1]) is int:
        return anom[1]
    else:
        months = ["jul", "aug", "sep", "oct", "nov", "dec", "jan", "feb", "mar", "apr", "may", "jun"]
        return months.index(anom[1])

filter("regional wa region", "region", "all", "all", "all")