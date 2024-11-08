import pandas as pd
import pymongo
from pymongo import MongoClient
import json
from statistics import mode
from tkinter import messagebox, Tk, Button
import matplotlib.pyplot as plt
import seaborn as sns

#Defining here for simplicity and re-usability
multiplexes = ['C18A', 'C18F', 'C188']

def clean_data(file_path):
    data1 = pd.read_csv(file_path["Antenna"])
    #having to use Latin1 for encoding as when I initially read the .csv file from utf-8 I was 
    #getting an error
    data2 = pd.read_csv(file_path["Params"], encoding='latin1')

    #merging on the first ID column as they share the same ID
    merged_data = pd.merge(data1, data2, on='id', how='outer')

    #Changing 'Freq.' to 'Freq' as the former was causing issues.
    merged_data.rename(columns={"Freq.": "Freq"}, inplace=True)
    # Task 1
    exclude_these_values = ['NZ02553847', 'SE213515', 'NT05399374', 'NT252675908']
    merged_data = merged_data[~merged_data['NGR'].isin(exclude_these_values)]

    # Task 2
    # Extract the multiplex block (C18A, C18F, C188) from the 'EID' column
    merged_data['Multiplex'] = merged_data['EID'].apply(lambda x: x[:4] if isinstance(x, str) else None)

    # Create a new column for each multiplex category
    
    for multiplex in multiplexes:
        merged_data[multiplex] = merged_data['Multiplex'].apply(lambda x: 'Yes' if x == multiplex else 'No')

    # Rename 'In-Use Ae Ht' and 'In-Use ERP Total' to 'Aerial height (m)' and 'Power (kW)' as per request
    merged_data['Aerial height (m)'] = merged_data['In-Use Ae Ht']
    merged_data['Power (kW)'] = merged_data['In-Use ERP Total']

    # Drop the old columns as these are no longer needed. 
    merged_data.drop(['In-Use Ae Ht', 'In-Use ERP Total'], axis=1, inplace=True)

    # Task 3 - HUGE TASK
    # Convert 'Date' column to datetime to filter by year
    # Extracting the year using string slicing, I am also saving it to a new column
    #so that it is easier to compare and use that Year instead of the full date.
    #I am also filling in any NaN values with 1900 just to reduce errors
    merged_data['Year'] = merged_data['Date'].str[-4:].fillna('1900').astype(int)  
    #I was having issues with power being treated as an int due to th ecomma delimeter, I just removed hte comma
    #and put it as a number here so 1.018,472 would convert to 1.018472 for example
    merged_data['Power (kW)'] = merged_data['Power (kW)'].str.replace(',', '').apply(pd.to_numeric, errors='coerce')

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

    # Task 4 - HUGE TASK

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

    # Save to JSON for future readability, it's better only printing to terminal in my opinion.
    with open("numerical_statistics_for_power.json", "w") as file:
        json.dump(stats_results, file, indent=4)

def visualize_multiplex_data():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/") 
    db = client['dab_database']
    collection = db['dab_data']
    
    # Query data for the relevant multiplexes: C18A, C18F, C188

    query = {"Multiplex": {"$in": multiplexes}}
    
    # Retrieve the necessary fields
    projection = {
        "Site": 1, 
        "Freq": 1,
        "Block": 1,
        "Serv Label1": 1,
        "Serv Label2": 1,
        "Serv Label3": 1,
        "Serv Label4": 1,
        "Serv Label10": 1,
        "Multiplex": 1
    }
    
    data = collection.find(query, projection)
    
    # Convert MongoDB cursor to pandas DataFrame
    df = pd.DataFrame(list(data))
    
    # Drop rows with missing multiplex or service labels
    df.dropna(subset=["Multiplex"], inplace=True)
    
    # Plot the data
    plot_data(df)
    
def plot_data(df):
    
    # 1. Number of Sites per Multiplex - Bar Plot
    multiplex_site_count = df.groupby('Multiplex')['Site'].nunique()  # Count unique sites for each multiplex
    plt.figure(figsize=(8, 6))
    multiplex_site_count.plot(kind='bar', color='lightgreen')
    plt.title('Number of Sites per Multiplex')
    plt.xlabel('Multiplex')
    plt.ylabel('Unique Site Count')
    plt.xticks(rotation=0)
    plt.show()
    
    # 2. Frequency per Multiplex - Bar Plot
    multiplex_freq = df.groupby('Multiplex')['Freq'].first()  # Assuming the frequency is the same per multiplex
    plt.figure(figsize=(8, 6))
    multiplex_freq.plot(kind='bar', color='salmon')
    plt.title('Frequency per Multiplex')
    plt.xlabel('Multiplex')
    plt.ylabel('Frequency (MHz)')
    plt.xticks(rotation=0)
    plt.show()
    
    # 3. Number of Blocks per Multiplex - Bar Plot
    multiplex_block_count = df.groupby('Multiplex')['Block'].nunique()  # Count unique blocks for each multiplex
    plt.figure(figsize=(8, 6))
    multiplex_block_count.plot(kind='bar', color='lightblue')
    plt.title('Number of Blocks per Multiplex')
    plt.xlabel('Multiplex')
    plt.ylabel('Unique Block Count')
    plt.xticks(rotation=0)
    plt.show()

    # 4. Service Label Distribution across Multiplexes - Stacked Bar Plot
    # Prepare a dictionary to store the count of each service label per multiplex
    service_labels = ['Serv Label1', 'Serv Label2', 'Serv Label3', 'Serv Label4', 'Serv Label10']

    # Prepare a dictionary to store the count of each service label per multiplex
    service_label_counts = {label: [] for label in service_labels}

    # For each multiplex, count how many of each service label appear
    for multiplex in multiplexes:
        multiplex_data = df[df['Multiplex'] == multiplex]
        for label in service_labels:
            # Count occurrences of each service label in the multiplex
            label_count = multiplex_data[label].notna().sum()  # Count non-null values for each label
            service_label_counts[label].append(label_count)
    
    # Convert the counts dictionary to a DataFrame for easy plotting
    service_label_counts_df = pd.DataFrame(service_label_counts, index=multiplexes)
    
     # Get a color palette with the same number of colors as there are service labels
    colors = sns.color_palette("Set2", n_colors=len(service_labels))
    
    # Plot the data: Stack the bars to show counts of each service label in each multiplex
    ax = service_label_counts_df.plot(kind='bar', stacked=True, figsize=(10, 6), color=colors)
    
    # Customizing the plot
    plt.title('Service Label Distribution across Multiplexes')
    plt.xlabel('Multiplex')
    plt.ylabel('Count of Service Labels')
    plt.xticks(rotation=0)
    # Ensure the legend has the correct colors and labels
    # `handles` are the plotted bars, `labels` are the service label names
    handles, labels = ax.get_legend_handles_labels()
    
    # Set the correct labels for the legend
    ax.legend(handles=handles, labels=service_labels, title='Service Labels', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adjust layout to avoid clipping the legend
    plt.tight_layout()  # Ensure the layout is tight for better display
    
    # Display the plot
    plt.show()

# Task 5- HUGE TASK

# Function to preprocess and clean the data for correlation analysis
def preprocess_data(df):
    # Ensure that 'Freq' and 'Block' are numeric. If they aren't, convert them.
    df['Freq'] = pd.to_numeric(df['Freq'], errors='coerce')
    df['Block'] = pd.to_numeric(df['Block'], errors='coerce')
     # Remove any leading or trailing spaces from column names as this was casuing errors.
    df.columns = df.columns.str.strip() 
    

    # Encode service labels as binary (1 for non-null, 0 for null)
    service_labels = ['Serv Label1', 'Serv Label2', 'Serv Label3', 'Serv Label4', 'Serv Label10']
    
    for label in service_labels:
        df[label] = df[label].notna().astype(int)  # 1 if label is present, 0 if not

    return df


# Function to calculate and display correlation matrix
def calculate_correlation(df):
    # Selecting relevant columns for correlation
    cols = ['Freq', 'Block'] + ['Serv Label1', 'Serv Label2', 'Serv Label3', 'Serv Label4', 'Serv Label10']
    
    # Calculate the correlation matrix
    correlation_matrix = df[cols].corr()

    return correlation_matrix

# Function to plot correlation matrix heatmap
def plot_correlation_heatmap(correlation_matrix):
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
    plt.title("Correlation Heatmap of Frequency, Block, and Service Labels")
    plt.show()

# Function to analyze correlation between columns
def analyze_correlation(df):
    # Preprocess the data (convert service labels and Freq/Block to numeric if necessary)
    df_processed = preprocess_data(df)
    
    # Calculate the correlation matrix
    correlation_matrix = calculate_correlation(df_processed)
    
    # Visualize the correlation using a heatmap
    plot_correlation_heatmap(correlation_matrix)


file_path = {
    "Antenna": "TxAntennaDAB.csv",
    "Params": "TxParamsDAB.csv"
}

cleaned_data = clean_data(file_path)
printStats(cleaned_data)
visualize_multiplex_data()
analyze_correlation(cleaned_data)