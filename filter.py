import csv, sqlite3, os, pandas

# Desktop (windows) works for relative addresses for some reason, Mac doesn't
# Desktop location: C:/Users/User/OneDrive/Uni/CITS3200/WA-Crime/data.db
# Mac location /Users/blank/OneDrive/Uni/CITS3200/WA-Crime/data.db

def filter(name, zone, year, mq, offence):

    database = "data.db"
    crime_file = "crime.csv"
    localities_file = "localities.csv"

    # Year_fn is financial year starting year. Do not need to store the
    # following year - it is implied. Use of integer makes for easier
    # comparison.
    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS Crime (
                                        Suburb text NOT NULL,
                                        Crime text NOT NULL,
                                        Year_fn int NOT NULL,
                                        Jul int,
                                        Aug int,
                                        Sep int,
                                        Oct int,
                                        Nov int,
                                        Dec int,
                                        Jan int,
                                        Feb int,
                                        Mar int,
                                        Apr int,
                                        May int,
                                        Jun int,
                                        Annual int
                                    ); """

    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS Localities (
                                    Suburb text PRIMARY KEY NOT NULL,
                                    Station text NOT NULL,
                                    District text NOT NULL,
                                    Region text NOT NULL
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
    query = ""
    mrange = ""
    y1, y2 = 0, 0
    
    if mq != 'all':
        mrange = str(distribution(mq))
    else:
        # We assume no more updates to the calendar system
        mq = "Jul-Jun"
        mrange = str(distribution(mq))

    if year != 'all':
        y1, y2 = yrange(year)
    else:
        # In-built Y3K bug
        y1, y2 = 0, 3000
    # query += "SELECT " + zone + ", " + mrange + " AS Total FROM Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb"
    # query += "SELECT Crime." + zone + ", " + mrange + " AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb) WHERE Crime.Suburb = '" + name + "'"
    
    # Determines subordinate zone type for selection and grouping (This feature may be made redundant in the future in favour of a custom zone selection)
    zones = ['Suburb', 'Station', 'District', 'Region']
    sub_zone = ""

    # All selection for zone defaults to suburb, also resets sub_zone and name to 'all' so that all suburbs are selected.
    if zone == 'all' or zone == 'Suburb':
        zone = 'Suburb'
        sub_zone = 'Suburb'
        name = 'all'

    # When name is 'all', we return all of that zone type, therefore no subzones. When name is not all, we return only the named zone and it's subzones.
    if name != 'all':
        sub_zone = zones[zones.index(zone) - 1]
    else:
        sub_zone = zone

    # Below is for a more descriptive query result
    # query += "SELECT Localities." + sub_zone + ", " + "Crime, Year_fn, Localities." + zone + ", SUM(" + mrange + ") AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb)"

    query += "SELECT Localities." + sub_zone + ", SUM(" + mrange + ") AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb)"
    # CURRENT PROBLEM. LEAKS AROUND YEAR_FN REQUIRING YOU INCLUDE PREVIOUS OR FOLLOWING YEARS
    if name != 'all' or offence != 'all' or year != 'all':
        query += " WHERE"
        # includeand to check if query has multiple conditions, so that "AND" can be appended to include them
        includeand = False
        if name != 'all':
            query += " Localities." + zone + " = '" + name.lower() + "'"
            includeand = True
        if offence != 'all':
            if includeand:
                query += " AND"
            query += " Crime = '" + offence.lower() + "'"
            includeand = True
        if year != 'all':
            if includeand:
                query += " AND"
            query += " Year_fn >= " + y1 + " AND Year_fn < " + y2
    if sub_zone == 'Suburb':
        query += " GROUP BY Year_fn, Localities." + sub_zone + " ORDER BY Localities." + sub_zone
    else:
        query += " GROUP BY Year_fn, " + sub_zone + " ORDER BY " + sub_zone

    # # All crime type all year type
    # query += "SELECT Localities." + sub_zone + ", " + "Crime, Year_fn, Localities." + zone + ", SUM(" + mrange + ") AS Total FROM (Crime LEFT OUTER JOIN Localities ON Crime.Suburb = Localities.Suburb)"
    # # CURRENT PROBLEM. YEAR_FN IS ISNT PROPERLY INT FORM, CANT DO COMPARISON 
    # query += " WHERE Localities." + zone + " = '" + name.lower() + "'"
    # query += " GROUP BY Year_fn, " + sub_zone + " ORDER BY " + sub_zone

    print(query)
    
    # Print output to command line
    c.execute(query)
    j = 0
    output = []
    for i in c.fetchall():
        output.append(list(i))
        print(j, i)
        j += 1
    # print(c.fetchall())

    print(query)
    return output

def distribution(mq):
    # Collects the months whose data are to be summed, scans from m0 to m1 collecting
    # months in between.
    months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    query = ""
    if mq != 'all':
        # Quarters not done yet
        if mq[0] == 'Q':
            e = 4
        mrange = "("
        m0 = mq[0:3]
        # Index of first month so we can iterate through list
        mi = months.index(m0)
        m1 = mq[4:]
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

def yrange(year):
    y = year.split('-')
    print(y)
    return y[0], y[1]

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
    

# Name, zone, year, month/quarter, crime
filter('Mandurah', 'Station', '2012-2017', 'Jul-Oct', 'Stealing') 

#perth district = 92571, wembley station = 34120


