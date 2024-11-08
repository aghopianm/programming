import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
    #It is worth noting that Block will be empty here, Block returns 12B throughout
    #The entire dataset, and so in my opinion is slightly pointless here to even pot.
    plt.show()

# Function to analyze correlation between columns
def analyze_correlation(df):
    # Preprocess the data (convert service labels and Freq/Block to numeric if necessary)
    df_processed = preprocess_data(df)
    
    # Calculate the correlation matrix
    correlation_matrix = calculate_correlation(df_processed)
    
    # Visualize the correlation using a heatmap
    plot_correlation_heatmap(correlation_matrix)