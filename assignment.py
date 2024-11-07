import pandas as pd
import pymongo
from pymongo import MongoClient
import json
from statistics import mode
from tkinter import messagebox, Tk, Button
import matplotlib.pyplot as plt
import seaborn as sns

def clean_data(file_path):
    data1 = pd.read_csv("TxAntennaDAB.csv")
    #having to use Latin1 for encoding as when I initially read the .csv file from utf-8 I was 
    #getting an error
    data2 = pd.read_csv("TxParamsDAB.csv", encoding='latin1')

    #merging on the first ID column as they share the same ID
    merged_data = pd.merge(data1, data2, on='id', how='outer')

    # Task 1
    exclude_these_values = ['NZ02553847', 'SE213515', 'NT05399374', 'NT252675908']
    merged_data = merged_data[~merged_data['NGR'].isin(exclude_these_values)]

    # Task 2
    # Extract the multiplex block (C18A, C18F, C188) from the 'EID' column
    merged_data['Multiplex'] = merged_data['EID'].apply(lambda x: x[:4] if isinstance(x, str) else None)

    # Create a new column for each multiplex category
    multiplexes = ['C18A', 'C18F', 'C188']
    for multiplex in multiplexes:
        merged_data[multiplex] = merged_data['Multiplex'].apply(lambda x: 'Yes' if x == multiplex else 'No')

    # Rename 'In-Use Ae Ht' and 'In-Use ERP Total' to 'Aerial height (m)' and 'Power (kW)' as per request
    merged_data['Aerial height (m)'] = merged_data['In-Use Ae Ht']
    merged_data['Power (kW)'] = merged_data['In-Use ERP Total']

    # Drop the old columns as these are no longer needed. 
    merged_data.drop(['In-Use Ae Ht', 'In-Use ERP Total'], axis=1, inplace=True)

    # Task 3
    # Convert 'Date' column to datetime to filter by year
    # Extracting the year using string slicing, I am also saving it to a new column
    #so that it is easier to compare and use that Year instead of the full date.
    #I am also filling in any NaN values with 1900 just to reduce errors
    merged_data['Year'] = merged_data['Date'].str[-4:].fillna('1900').astype(int)  
    #I was having issues with power being treated as an int due to th ecomma delimeter, I just removed hte comma
    #and put it as a number here so 1.018,472 would convert to 1.018472 for example
    merged_data['Power (kW)'] = merged_data['Power (kW)'].str.replace(',', '').apply(pd.to_numeric, errors='coerce')

    # Apply filters for 'Site Height' > 75 and 'Year' >= 2001
    filtered_data = merged_data[
        (merged_data['Site Height'] > 75) &
        (merged_data['Year'] >= 2001) &
        (merged_data['Multiplex'].isin(multiplexes))  # Filter for the multiplexes
    ]

    #Calculations here and printing to console:
    mean_calculation = filtered_data['Power (kW)'].mean()
    mode_calculation = filtered_data['Power (kW)'].mode()[0]  # mode() returns a series, so first element is taken
    median_calculation = filtered_data['Power (kW)'].median()

    # Prepare results dictionary
    stats_results = {
        "Power (kW) Statistics": {
            "Mean": mean_calculation,
            "Mode": mode_calculation,
            "Median": median_calculation
        }
    }

    # Print the calculated statistics to the console
    print(f"Mean of 'Power (kW)': {mean_calculation}")
    print(f"Mode of 'Power (kW)': {mode_calculation}")
    print(f"Median of 'Power (kW)': {median_calculation}")

    # Save to JSON for future readability, it's better only printing to terminal in my opinion.
    with open("numerical_statistics_for_power.json", "w") as file:
        json.dump(stats_results, file, indent=4)

    #saving merged data JSON instead of an XML as XML is too verbose for this
    #I am also using lines=True as the dataset is relatively large so for readability
    merged_data.to_json("merged_data.json", orient='records', lines=False, indent=4)

    #Given how large the dataset is currently, and the complexity of our querying needs
    #I am going to now move this from a JSON file into mongoDB, it's also very efficient comparatively 
    #I have created a local version of this database instead of a cloud version
    client = MongoClient("mongodb://localhost:27017/") 

    db = client['dab_database']  # Use or create a database called 'dab_database'
    collection = db['dab_data']  # Use or create a collection called 'dab_data'

    collection.insert_many(merged_data.to_dict('records'))

    return merged_data

    # The following comments correspond to the "Data Manipulation" part of the assignmen(cleaning)t:

    # 1. Outputs should not include any data from DAB radio stations that have the
    # following ‘NGR’: NZ02553847, SE213515, NT05399374 and NT252675908
    #At this point I have opened up my mongo shell, and ran this script:
    #db.dab_data.find({"NGR": {"$in": ["NZ02553847", "SE213515", "NT05399374", "NT252675908"]}}) to check
    #and nothing was returned. This ensures that those entries with the NGR values above
    #have now been removed.

    # 2. The ‘EID’ column contains information of the DAB multiplex block...

    #to query the database you could run the following query on the MongoDB, this would show all
    #instances of where C18A, C18F or C188 is as the multiplex:
    #db.dab_data.find({
    #    $or: [
    #        { "C18A": "Yes" },
    #        { "C18F": "Yes" },
    #        { "C188": "Yes" }
    #    ]
    #}, {
    #    "NGR": 1, 
    #    "Site": 1,
    #    "Site Height": 1,
    #    "Aerial height (m)": 1,
    #    "Power (kW)": 1,
    #    "Multiplex": 1
    #}).limit(5)

file_path = {
    "Antenna": "TxAntennaDAB.csv",
    "Params": "TxParamsDAB.csv"
}

cleaned_data = clean_data(file_path)