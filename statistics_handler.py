import json
import pandas as pd
from pymongo import MongoClient
from data_processing import multiplexes

def printStats(merged_data):
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

    # Save to JSON for future readability, it's better to save for future use than just to print
    #to terminal
    with open("numerical_statistics_for_power.json", "w") as file:
        json.dump(stats_results, file, indent=4)