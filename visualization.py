import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from data_processing import multiplexes

def visualize_multiplex_data():
    # we need to connect to the database as we will be querying it for the multiplexes.
    client = MongoClient("mongodb://localhost:27017/") 
    db = client['dab_database']
    collection = db['dab_data']
    
    # Query data for the relevant multiplexes: C18A, C18F, C188
    query = {"Multiplex": {"$in": multiplexes}}
    
    # Retrieve the necessary fields as per the client requirement.
    fields = {
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
    
    data = collection.find(query, fields)
    
    # Convert MongoDB cursor to pandas DataFrame
    df = pd.DataFrame(list(data))
    
    # Drop rows with missing multiplex or service labels to avoid errors.
    df.dropna(subset=["Multiplex"], inplace=True)
    
    # Plot the data
    data_displayer(df)
    
def data_displayer(df):
    #We need to print a few graphs here, I am going to group the service labels but keep
    #the rest of them seperate.

    # 1. Number of Sites per Multiplex - Bar Plot
    multiplex_site_count = df.groupby('Multiplex')['Site'].nunique()  # Count unique sites for each multiplex
    plt.figure(figsize=(8, 6))
    multiplex_site_count.plot(kind='bar', color='red')
    plt.title('Number of Sites per Multiplex')
    plt.xlabel('Multiplex')
    plt.ylabel('Unique Site Count')
    plt.xticks(rotation=0)
    plt.show()
    
    # 2. Frequency per Multiplex - Bar Plot
    multiplex_freq = df.groupby('Multiplex')['Freq'].first()  # Assuming the frequency is the same per multiplex
    multiplex_freq.plot(kind='bar', color='blue')
    plt.title('Frequency per Multiplex')
    plt.xlabel('Multiplex')
    plt.ylabel('Frequency (MHz)')
    plt.xticks(rotation=0)
    plt.show()
    
    # 3. Number of Blocks per Multiplex - Bar Plot - There are no unique Blocks it is always
    # "12B"
    multiplex_block_count = df.groupby('Multiplex')['Block'].nunique()  # Count unique blocks for each multiplex
    plt.figure(figsize=(8, 6))
    multiplex_block_count.plot(kind='bar', color='orange')
    plt.title('Number of Blocks per Multiplex')
    plt.xlabel('Multiplex')
    plt.ylabel('Unique Block Count')
    plt.xticks(rotation=0)
    plt.show()

    # 4. Service Label Distribution across Multiplexes - Stacked Bar Plot
    # Prepare a dictionary to store the count of each service label per multiplex
    #as I am going to be plotting the counts
    service_labels = ['Serv Label1', 'Serv Label2', 'Serv Label3', 'Serv Label4', 'Serv Label10']

    # Prepare a dictionary to store the count of each service label per multiplex
    service_label_counts = {label: [] for label in service_labels}

    # For each multiplex, count how many of each service label appear
    for multiplex in multiplexes:
        multiplex_data = df[df['Multiplex'] == multiplex]
        for label in service_labels:
            # Count occurrences of each service label in the multiplex
            # Count non-null values for each label, i am not counting null values to avoid errors.
            label_count = multiplex_data[label].notna().sum()  
            service_label_counts[label].append(label_count)
    
    # Convert the counts dictionary to a DataFrame so I can pot without errors.
    service_label_counts_df = pd.DataFrame(service_label_counts, index=multiplexes)
    
     # Get a color palette with the same number of colors as there are service labels
    colors = sns.color_palette("Set2", n_colors=len(service_labels))
    
    # Plot the data: Stack the bars to show counts of each service label in each multiplex
    x = service_label_counts_df.plot(kind='bar', stacked=True, figsize=(10, 6), color=colors)
    
    # Customizing the plot
    plt.title('Service Label Distribution across Multiplexes')
    plt.xlabel('Multiplex')
    plt.ylabel('Count of Service Labels')
    plt.xticks(rotation=0)
    # Ensure the legend has the correct colors and labels
    # handles are the plotted bars and labels are the service label names
    handles, labels = x.get_legend_handles_labels()
    
    # Set the correct labels for the legend
    x.legend(handles=handles, labels=service_labels, title='Service Labels', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Ensure the layout is tight for better display
    plt.tight_layout() 
    
    plt.show()