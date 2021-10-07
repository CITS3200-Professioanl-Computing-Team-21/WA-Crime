# WA crime front-end branch
# Nat and Bo

# Folders
config -> csv for selector dropdown options\
tools -> supporting applications\
depre -> past versions of application

# Features
- Direct search via query
- Save as map as jpg
Selectors based on selector2.doc, adjustable via ./config csv
- Zone selectors for Suburb, Station, District, Region
- Time selectors Year, Month, Quarter
- Crime selector

# Versions
v 3.1 (integration patch)\
- Changed config/ .csv to be consistent with back end
- Query is now comma deliminated
- Error checking logic for period selectors
- Selectors respond to other selected options
- Query search error checking
- Prompt format for query search
- Dropdown query copied into query search box for copy/edit

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

v 0.5\
- Jup_selectors.ipynb -> Html generation using selectors in Jupyter
- PyQt html display.py -> input folium html file, displayed in PyQt application

# HTML files used for testing
districts.html\
regions.html\
stations.html\
testlayer.html\
testpin.html\
