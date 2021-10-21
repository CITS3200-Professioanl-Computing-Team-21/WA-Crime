# Getting started
# Program is running under conda enviornment

1. Creating a new geo_env 
   conda create -n geo_env
   conda activate geo_env
   conda config --env --add channels conda-forge
   conda config --env --set channel_priority strict
   conda install python=3 geopandas
   
2. Under conda virtual enviornment install dependencies
   Use "conda install or conda install -c conda-forge {package}" to install following dependencies
   1.Folium
   2.Geopandas
   3.PyQt
   4.Geojson
   5.Geopy
   
   - Not necessary but maybe needed
     Fuzzywuzzy
     Haversine
     
3. Then in conda-evn
   run --python app.py


# WA Crime back-end branch
# Sean, Aditya, Zak

# Versions
V 2.7\
- map.py -> localities summed and categorised one level down
         -> e.g. stations will be summed and categorised under district
         -> e.g. districts will be summed and categorised under region
V 2.6\
- map.py -> script able to query 'all' selectors

v 2.5\
- map.py -> script able to query different localities types

v 2.0\
- map.py -> script modified to handle selectors2.docx queries

v 1.5\
- map.py -> redone and optimised the script for future changes
- api.py -> collects coordinates for suburbs online
- boundaries.py -> compiles coordinates for different boundaries

v 1.0\
- map.py -> converts raw data into usable data for plotting and analysis

# Datasets used
- Locality_Data_Filtered (from Quart Website Rep Mar213-2.csv
- Localities_LGATE_234_WA_GDA2020_Public.geojson
- Suburb Locality.csv
- Coordinates.json -> generated from api.py
# WA crime front-end branch
# Nat and Bo

# Files
config -> csv for selector dropdown options\
images -> images used in style sheet\
app.py -> runs main application, contains main application logic
UI_3.5.ui -> file used by PyQt5 designer to generate ui.py
ui.py -> modified version of the generated file, containing style sheets

# Features
- Direct search via query
- Save as map as jpg
Selectors based on selector2.doc, adjustable via ./config csv
- Zone selectors for Suburb, Station, District, Region
- Time selectors Year, Month, Quarter
- Crime selector

# Versions
v 4.0 (final version)
- UI stylesheet added
- Functionailities for textual and graphical display of anomolies
- Threaded backend map generation for client responsiveness
Note: ui.py is now a modified version from the base generated UI3.5.ui\

v 3.1 (integration patch)
- Changed config/ .csv to be consistent with back end
- Query is now comma deliminated
- Error checking logic for period selectors
- Selectors respond to other selected options
- Query search error checking
- Prompt format for query search
- Dropdown query copied into query search box for copy/edit
- Error messages for search box query

v 3.0 (implemented functionailities of v2.5 and variable name changes in .ui)\
Features: functional features of v2.0, updated to fit selector2.doc, removed adjustable font, added placeholders for anomaly display
- UI-V3.0-pyqt5.ui -> file used by PyQT designer
- app.py -> run this for application
- ui.py -> py file used by PyQT designer

v 2.5 (skeleton)\
Features: UI layout with selectors based on selector2.doc (from backend team), range dropdown of time selectors, suburbs search
- ui.py -> py file used by PyQT designer
- UI-V2.5-pyqt5.ui -> file used by PyQT designer
- app.py -> run this for application

v 2.0 (implemented functionailities of v1.5)\
Features: functional features of v1.5, searchable dropdown, adjustable dropdown from config csv, cross dropdown interaction
- .ui file from v1.5
- app.py -> run this for application
- ui.py -> py file used by PyQT designer

v 1.5 (skeleton)\
Features: UI layout with selectors based on selector.doc (from backend team), direct search query, adjustable font size, export jpg
- application_bo.py -> py file used by PyQT designer
- application.ui -> file used by PyQT designer
- main.py -> run this for application

v 1.0\
Features: basic draft of possible UI mockup for client meeting
- application.ui -> file used by PyQT designer
- application.py -> working file with UI functionailities (run this on for the application)

v 0.5
- Jup_selectors.ipynb -> Html generation using selectors in Jupyter
- PyQt html display.py -> input folium html file, displayed in PyQt application
