# todo user input for selecting filename
# todo user input for file destination
# todo create into an .exe
from tkinter.filedialog import askopenfilename

import pandas as pd
import lvm_read
import numpy as np
import pandas as pd
from datetime import datetime
import tkinter
from tkinter import filedialog
import os

"""
Starting with accelerometer data file 
create a dataframe using the data from the file
create timestamps based on starting time and dt
"""
# creating user window
root = tkinter.Tk()
root.withdraw()  # use to hide tkinter window


# this function will search for a file path
def search_for_file_path():
    currdir = os.getcwd()
    tempdir = filedialog.askdirectory(parent=root, initialdir=currdir,
                                      title='Please select a folder to save your file to')
    if len(tempdir) > 0:
        print("You chose: %s" % tempdir)
    return tempdir


# file path as a variable
#file_path_variable = search_for_file_path()
file_path_variable = r'C:\Users\DanielCooper\Documents\Deck Sense Project\DAQ Data\Python Test Data'


# print ("\nfile_path_variable = ", file_path_variable)


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


# we don't want a full GUI, so keep the root window from appearing
tkinter.Tk().withdraw()

# show an "Open" dialog box and return the path to the selected file
# accelFile = askopenfilename(title='select ACCELEROMETER .lvm file')
# lcFile = askopenfilename(title='select LOAD CELL .lvm file')
# micFile = askopenfilename(title='select MICROPHONE .lvm file')
# scopeFile = askopenfilename(title='select OSCILLOSCOPE .lvm file')

userinput_number = input('Select Data Set Number: ')
if userinput_number == '0':
    userinput_number = ''
else:
    userinput_number = '_' + userinput_number

accelFile = r'C:\Users\DanielCooper\Documents\Deck Sense Project\DAQ Data\Python Test Data\Accels\accel_data' + userinput_number + '.lvm'
lcFile = r'C:\Users\DanielCooper\Documents\Deck Sense Project\DAQ Data\Python Test Data\LoadCells\load_cells_Data' + userinput_number + '.lvm'
micFile = r'C:\Users\DanielCooper\Documents\Deck Sense Project\DAQ Data\Python Test Data\Mics\mic_data' + userinput_number + '.lvm'
scopeFile = r'C:\Users\DanielCooper\Documents\Deck Sense Project\DAQ Data\Python Test Data\Scope\Power_data' + userinput_number + '.lvm'
torqueFile = r'C:\Users\DanielCooper\Documents\Deck Sense Project\DAQ Data\Python Test Data\Torque\torque_cell_Data' + userinput_number + '.lvm'

# "C:\Users\DanielCooper\Documents\Deck Sense Project\DAQ Data\Python Test Data\Torque\torque_cell_Data.lvm"

# naming the headers for each dataframe
accel_columns = ['Time', 'Accel_Left', 'Accel_Right', 'Accel_Center_X', 'Accel_Center_Y']
lc_columns = ['Time', 'LC0', 'LC1', 'LC2', 'LC3', 'LC4', 'LC5', 'LC6', 'LC7']
mic_columns = ['Time', 'Mic_Left_Front', 'Mic_Left_Back', 'Mic_Right_Back', 'Mic_Right_Front']
scope_columns = ['Time', 'Scope_Channel_0', 'Scope_Channel_1']
torque_columns = ['Time', 'Torque']


# create the dataframe format that we want for time sync up
def create_final_df(filename, columns, column_header):
    time_array = create_time_array(filename)
    data_array = create_data_array(filename)
    df = create_df(data_array, columns)
    create_time_column(time_array, df, column_header)
    return df


# creating the dataframes
header = 'Time'
accel_df = create_final_df(accelFile, accel_columns, header)
mic_df = create_final_df(micFile, mic_columns, header)
lc_df = create_final_df(lcFile, lc_columns, header)
scope_df = create_final_df(scopeFile, scope_columns, header)
torque_df = create_final_df(torqueFile, torque_columns, header)


# merge the files - the scope file is the reference file since it is the fastest sampling rate
def merge_df(accel_dataframe, mic_dataframe, lc_dataframe, scope_dataframe, torque_dataframe, how_Arg):
    # files are merged using the Time column
    merge1 = scope_dataframe.merge(mic_dataframe, how=how_Arg, on=['Time'])
    merge2 = merge1.merge(accel_dataframe, how=how_Arg, on=['Time'])
    merge3 = merge2.merge(lc_dataframe, how=how_Arg, on=['Time'])
    merge4 = merge3.merge(torque_dataframe, how=how_Arg, on=['Time'])
    return merge4


# merge dataframes
merged_df = merge_df(accel_df, mic_df, lc_df, scope_df, torque_df, 'outer')
# get rid of data that does not have scope reference
merged_df = merged_df[merged_df['Scope_Channel_0'].notna()]

# create csv file of the merged data and send to the loaciton that the user has selected
merged_df.to_csv(file_path_variable + '\merged_dataset.csv')

