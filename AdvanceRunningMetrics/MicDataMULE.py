import pandas as pd
import matplotlib.pyplot as plt


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
print(df.head())

# Scale y-values by 100
df[1] *= 100

# Plotting the scaled data
plt.plot(df[0], df[1], marker='o', linestyle='-')
plt.xlabel('Time')
plt.ylabel('Y values (scaled by 100)')
plt.title('Your Data Plot (Y values scaled by 100)')
plt.grid(True)


plt.show()