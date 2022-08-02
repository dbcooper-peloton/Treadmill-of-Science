# todo create a python script to combine all csv files
# create timestamps by using dt and start time in the excel file
# put into one csv file by lining up timestamps

import pandas as pd
import lvm_read
import numpy as np
import pandas as pd
from datetime import datetime

"""
Starting with accelerometer data file 
create a dataframe using the data from the file
create timestamps based on starting time and dt
"""


# create time array by reading in file and grabbing starting time
def create_time_array(filename):
    # read in file
    lvm = lvm_read.read(filename, read_from_pickle=False)
    time_array_temp = lvm[0]['Time']
    return time_array_temp


# create data array by reading in file and grabbing voltage readings
def create_data_array(filename):
    # read in file
    lvm = lvm_read.read(filename, read_from_pickle=False)
    data_array_temp = lvm[0]['data']
    return data_array_temp


# create dataframe using data array that contains voltage readings
def create_df(data_array, columnsArray):
    df = pd.DataFrame(data_array, columns=columnsArray)
    return df


# this function will convert the time column into seconds for easy sync up
# it will also take the start time and add the delta time to the start time to create a timestamp for each data point
def create_time_column(time_array, df, header):
    # convert start time to datetime format so that we can add dt
    time = time_array[0]

    # remove extra decimal places
    size = len(time)
    mod_time = time[:size - 13]

    # convert to datetime
    final_time = datetime.strptime(mod_time, '%H:%M:%S.%f')

    # convert to seconds
    a_timedelta = final_time - datetime(1900, 1, 1)
    seconds = a_timedelta.total_seconds()

    # add start time to accel time column (timestamping)
    df[header] = df[header] + seconds


# file to read in
#userinput = input('Enter Data Set Number: ')
#print('Number:' + userinput)
accelFile = r'C:\Users\DanielCooper\Documents\DAQ Data\Python Test Data\Accels\accel_data_2.lvm'
lcFile = r'C:\Users\DanielCooper\Documents\DAQ Data\Python Test Data\LoadCells\load_cells_Data_2.lvm'
micFile = r"C:\Users\DanielCooper\Documents\DAQ Data\Python Test Data\Mics\mic_data_2.lvm"
scopeFile = r"C:\Users\DanielCooper\Documents\DAQ Data\Python Test Data\Scope\Power_data_2.lvm"

# naming the headers for each dataframe
accel_columns = ['Time', 'Accel_Left', 'Accel_Right', 'Accel_Center_X', 'Accel_Center_Y']
lc_columns = ['Time', 'LC0', 'LC1', 'LC2', 'LC3', 'LC4', 'LC5', 'LC6', 'LC7']
mic_columns = ['Time', 'Mic_Left_Front', 'Mic_Left_Back', 'Mic_Right_Back', 'Mic_Right_Front']
scope_columns = ['Time', 'Scope_Channel_0', 'Scope_Channel_1']


# create the dataframe format that we want for time sync up
def create_final_df(filename, columns, header):
    time_array = create_time_array(filename)
    data_array = create_data_array(filename)
    df = create_df(data_array, columns)
    create_time_column(time_array, df, header)
    return df

#creating the dataframes
header = 'Time'
acceldf = create_final_df(accelFile, accel_columns, header)
micdf = create_final_df(micFile, mic_columns, header)
lcdf = create_final_df(lcFile, lc_columns, header)
scopedf = create_final_df(scopeFile, scope_columns, header)


# print(acceldf)
# print(micdf)
# print(lcdf)
# print(scopedf)

# todo: create function to combine dataframes based on first column

# merge the files - the scope file is the reference file since it is the fastest sampling rate
def merge_df(acceldf, micdf, lcdf, scopedf, howArg):
    # files are merged using the Time column
    merge1 = scopedf.merge(micdf, how=howArg, on=['Time'])
    merge2 = merge1.merge(acceldf, how=howArg, on=['Time'])
    merge3 = merge2.merge(lcdf, how=howArg, on=['Time'])
    return merge3

#merge dataframes
merged_df = merge_df(acceldf, micdf, lcdf, scopedf, 'outer')
# get rid of data that does not have scope reference
merged_df = merged_df[merged_df['Scope_Channel_0'].notna()]

#print(merged_df)
#create csv file of the merged data
merged_df.to_csv(r'C:\Users\DanielCooper\PycharmProjects\pythonProject2\merged_df.csv')
