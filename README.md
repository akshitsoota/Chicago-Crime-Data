# Chicago Crime Data

![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python 2.7.12](https://img.shields.io/badge/python-2.7.12-lightgrey.svg)

The data is retreived from [City of Chicago - Crimes from 2001 to present](https://data.cityofchicago.org/Public-Safety/Crimes-2001-to-present/ijzp-q8t2).
The data dumps uploaded is for crimes dating from 01/01/2001 to 11/28/2016.

### Script - [dataprocessor.py](https://github.com/akshitsoota/Chicago-Crime-Data/blob/master/dataprocessor.py)

This script helps selectively extrapolate data from the original data source.

`extract` is a dictionary with the key being name of the folder and the value being a list of lists. A few examples are as follows:

```python
# To extract crimes based on the description along with the month and the year
extract = {"desc_month_year": [['Primary Type', []],
                               ['Date', [(0, 2), (6, 10)]]]}
# (0 to 2) and (6 to 10) are called split points.
# Because the dates are of the format "mm/dd/yyyy", value extract from Date is "mmyyyy"

# To extract crimes in various months independent of the year
extract = {"month": [['Date', [(0, 2)]]]}

# To extract crimes based on Police Beats for each year
extract = {"beat_year": [['Beat', []],
                         ['Date', [(6, 10)]]]}
                         
# Combining all of the above, could yield in
extract = {"desc_month_year": [['Primary Type', []],
                               ['Date', [(0, 2), (6, 10)]]],
           "month": [['Date', [(0, 2)]]],
           "beat_year": [['Beat', []],
                         ['Date', [(6, 10)]]]}
```

`flex` refers to the file extensions that will be generated along with the fields that the file would contain. A few examples are as follows:

```python
# To extract crimes with just the fields ID, Date, Primary Type and Beat into 
#   files with the name "..._condensed.json"
flex = {"_condensed": ["ID", "Date", "Primary Type", "Beat"]}

# To extract two files, one with all the crime information and the other only with selective fields
flex = {"_all": [],
        "_condensed": ["ID", "Date", "Primary Type", "Beat"]}
```

`conditions` is a dictionary of lambda functions to decide whether to proceed with a certain crime. A few examples are as follows:

```python
# To extract all possible crimes
conditions = {}
# OR
conditions = {"_": lambda _, __: True}

# To extract, all crimes if the folder name is "beat_year" but only crimes from 2016 in the "month" folder:
conditions = {"year_classifier": 
              lambda folder_name, row: 
                     folder_name == "beat_year" or 
                     (folder_name == "month" and row[2][6:10] == "2016")
             }
```

### Script - [beatprocessor.py](https://github.com/akshitsoota/Chicago-Crime-Data/blob/master/beatprocessor.py)
This script extracts crime counts against different types of crimes, classified by beat number (within each file), month and year
(by different files). The key `__beatordering` in the file gives the required ordering for the beat counts.
