import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt

# Define the path to the dataset directory
#DataRootDir = r'C:\Users\cooper\Documents\EE_STM\Advance_Running_Metrics\Emily'
#Dname = r'0Inc_0.8MPH'
#Dname = DataRootDir + '\\' + Dname
#print(Dname)

# Replace 'your_file.xlsx' with the path to your Excel file
file_path = r'C:\Users\cooper\Documents\EE_STM\Advance_Running_Metrics\Emily\0Inc_0.8MPH.csv'

# Read the CSV file
df = pd.read_csv(file_path, low_memory=False)

# Read the CSV file, skipping the header and the first three rows
df = pd.read_csv(file_path, header=None, skiprows=4)

# Display the first few rows of the DataFrame
# print(df.head())

#print(len(df))
#subset_df = df.head(250000)

# Extract voltage data from the second column
voltage_data = df.iloc[:, 1]

# Define the sampling frequency (Hz) and cutoff frequency for the filter (Hz)
sampling_freq = 1000  # Example: 1000 Hz
cutoff_freq = 50  # Example: 50 Hz

# Normalize cutoff frequency to Nyquist frequency
normalized_cutoff_freq = cutoff_freq / (0.5 * sampling_freq)

# Define the filter order
filter_order = 4  # Example: 4

# Design the Butterworth filter
b, a = butter(filter_order, normalized_cutoff_freq, btype='low', analog=False)

# Apply the filter to the dataframe
filtered_df = df.apply(lambda x: filtfilt(b, a, x) if x.name != 0 else x)

# Display the filtered dataframe
#print(filtered_df)

# Initialize variables to track subset start and stop indices
start_index = None
subset_dfs = []

# Iterate through the voltage data
for index, row in filtered_df.iterrows():
    if row[1] > -0.05:  # Assuming the voltage column is at index 1
        if start_index is None:
            start_index = index
    elif start_index is not None:
        # Create subset dataframe from start_index to current index
        subset_df = filtered_df.iloc[start_index:index+1]
        subset_df.columns = ["TIME", "VOLTAGE"]  # Adding column names
        subset_dfs.append(subset_df)
        start_index = None

        # Add a marker row between subset dataframes
        marker_row = pd.DataFrame([['', '']], columns=["TIME", "VOLTAGE"])
        subset_dfs.append(marker_row)

# If the last subset ends with a value above -0.05, include it as well
if start_index is not None:
    subset_df = filtered_df.iloc[start_index:]
    subset_df.columns = ["TIME", "VOLTAGE"]  # Adding column names
    subset_dfs.append(subset_df)

    # Add a marker row after the last subset dataframe
    marker_row = pd.DataFrame([['', '']], columns=["TIME", "VOLTAGE"])
    subset_dfs.append(marker_row)

# Concatenate the subset dataframes and marker rows
result_df = pd.concat(subset_dfs, ignore_index=True)

# Display the subset dataframe
# print(result_df)

def count_breaks(df):
    """
    Count the number of breaks (marker rows) in the concatenated dataframe.

    Parameters:
    - df: Concatenated dataframe with marker rows between subset dataframes.

    Returns:
    - count: Number of breaks (marker rows) found in the dataframe.
    """
    count = np.sum(df["TIME"] == '')
    return count


def plot_subset_by_break(df, break_index):
    """
    Plot a subset dataframe based on the break index.

    Parameters:
    - df: Concatenated dataframe with marker rows between subset dataframes.
    - break_index: Index of the break (marker row) indicating the subset dataframe to plot.
    """
    # Find indices of breaks (marker rows)
    break_indices = df.index[df["TIME"] == ''].tolist()

    # Ensure break_index is within the range of breaks
    if break_index < 0 or break_index >= len(break_indices):
        print("Invalid break index.")
        return

    # Determine start and end indices of the subset dataframe to plot
    start_index = break_indices[break_index] + 1 if break_index > 0 else 0
    end_index = break_indices[break_index + 1] if break_index + 1 < len(break_indices) else len(df)

    # Clean the dataframe by removing empty strings in the "TIME" column
    clean_df = df[df["TIME"] != '']

    # Plot the subset dataframe
    plt.figure(figsize=(10, 5))
    plt.plot(clean_df["TIME"][start_index:end_index].astype(float),
             clean_df["VOLTAGE"][start_index:end_index].astype(float), color='b')
    plt.xlabel("Time")
    plt.ylabel("Voltage")
    plt.title("Subset DataFrame {} (Break {})".format(break_index + 1, break_index))
    plt.grid(True)
    plt.show()

def plot_concatenated_dataframe(df):
    """
    Plot the concatenated dataframe.

    Parameters:
    - df: Concatenated dataframe with marker rows between subset dataframes.
    """
    # Clean the dataframe by removing empty strings in the "TIME" column
    clean_df = df[df["TIME"] != '']

    # Plot the entire concatenated dataframe
    plt.figure(figsize=(10, 5))
    plt.plot(clean_df["TIME"].astype(float), clean_df["VOLTAGE"].astype(float), color='b')
    plt.xlabel("Time")
    plt.ylabel("Voltage")
    plt.title("Concatenated DataFrame")
    plt.grid(True)
    plt.show()

# Example usage:
# plot_concatenated_dataframe(result_df)

# Example usage:
# Count the number of breaks in the concatenated dataframe
num_breaks = count_breaks(result_df)
print("Number of breaks:", num_breaks)

# Plot a subset dataframe based on break index (e.g., break 0)
plot_subset_by_break(result_df, 22)
