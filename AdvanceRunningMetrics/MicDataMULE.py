import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt

def read_csv_file(file_path):
    """Read CSV file and return DataFrame."""
    return pd.read_csv(file_path, low_memory=False)

def filter_dataframe(df, cutoff_freq=50, sampling_freq=1000, filter_order=4):
    """Apply Butterworth filter to DataFrame."""
    normalized_cutoff_freq = cutoff_freq / (0.5 * sampling_freq)
    b, a = butter(filter_order, normalized_cutoff_freq, btype='low', analog=False)
    return df.apply(lambda x: filtfilt(b, a, x) if x.name != 0 else x)

def find_break_indices(df):
    """Find indices of breaks (marker rows) in DataFrame."""
    return df.index[df["TIME"] == ''].tolist()

def clean_dataframe(df):
    """Remove empty strings in the 'TIME' column."""
    return df[df["TIME"] != '']

def plot_subset_dataframe(df, start_index, end_index):
    """Plot a subset dataframe."""
    plt.figure(figsize=(10, 5))
    plt.plot(df["TIME"].astype(float)[start_index:end_index],
             df["VOLTAGE"].astype(float)[start_index:end_index], color='b')
    plt.xlabel("Time")
    plt.ylabel("Voltage")
    plt.title("Subset DataFrame")
    plt.grid(True)
    plt.show()

def plot_concatenated_dataframe(df):
    """Plot the concatenated dataframe."""
    clean_df = clean_dataframe(df)
    plt.figure(figsize=(10, 5))
    plt.plot(clean_df["TIME"].astype(float), clean_df["VOLTAGE"].astype(float), color='b')
    plt.xlabel("Time")
    plt.ylabel("Voltage")
    plt.title("Concatenated DataFrame")
    plt.grid(True)
    plt.show()


def count_breaks(df):
    """Count the number of breaks (marker rows) in the concatenated dataframe."""
    return np.sum(df["TIME"] == '')

def plot_subset_by_break(df, break_index):
    """Plot a subset dataframe based on the break index."""
    break_indices = find_break_indices(df)
    if break_index < 0 or break_index >= len(break_indices):
        print("Invalid break index.")
        return
    start_index = break_indices[break_index] + 1 if break_index > 0 else 0
    end_index = break_indices[break_index + 1] if break_index + 1 < len(break_indices) else len(df)
    clean_df = clean_dataframe(df)
    plot_subset_dataframe(clean_df, start_index, end_index)

# Replace 'your_file.xlsx' with the path to your Excel file
file_path = r'C:\Users\cooper\Documents\EE_STM\Advance_Running_Metrics\Emily\0Inc_0.8MPH.csv'

# Read the CSV file
df = read_csv_file(file_path)

# Read the CSV file, skipping the header and the first three rows
df = pd.read_csv(file_path, header=None, skiprows=4)

# Filter the dataframe
filtered_df = filter_dataframe(df)

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
print(result_df)

# Graph concatenated dataframe
# plot_concatenated_dataframe(result_df)

# Count how many footsteps there are
# num_breaks = count_breaks(result_df)
# print("Number of footsteps:", num_breaks)

# Plot a single footstep
# plot_subset_by_break(result_df, 25)
# plot_subset_by_break(result_df, 26)
# plot_subset_by_break(result_df, 27)

