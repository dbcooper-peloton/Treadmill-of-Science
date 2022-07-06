from csv import writer
from datetime import datetime
import time
import pandas as pd
import numpy as np
import pyvisa
import threading
from NI_DAQ_Library import NIDAQ
from OMEGA_Library import OM_USB_ADC
from Tektronix_Library import DPO2024B
import multiprocessing

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# This function acquires Accelerometer(NI Daq) data
# and adds them to an array with a timestamp. This array will be written to a csv in main loop
def acquire_Tek(Tek):
    # get current timestamp
    now = datetime.now()
    # current date and time
    dt = now.strftime("%m/%d/%Y, %H:%M:%S.%f")[:-3]

    # Create array to hold a row of data and put timestamp in index 0
    dataRow = np.array([dt])
    
    # Get waveform RMS from the scope channel 1 and append to the array
    rms = Tek.waveform_rms(1)
    dataRow = np.append(dataRow, str(rms))
    
    return dataRow


# This function acquires Accelerometer(NI Daq) data
# and adds them to an array with a timestamp. This array will be written to a csv in main loop
def acquire_Omega(Omega, channelNum):
    # get current timestamp
    now = datetime.now()
    # current date and time
    dt = now.strftime("%m/%d/%Y, %H:%M:%S.%f")[:-3]

    # Create array to hold a row of data and put timestamp in index 0
    dataRow = np.array([dt])

    # insert_channel from 0 up to 7
    dataRow = np.append(dataRow, Omega.voltage_reading(channel=channelNum))

    return dataRow


# This function acquires Accelerometer(NI Daq) data
# and adds them to an array with a timestamp. This array will be written to a csv in main loop
def acquire_data_Accel(channelNum):
    # get current timestamp
    now = datetime.now()
    # current date and time
    dt = now.strftime("%m/%d/%Y, %H:%M:%S.%f")[:-3]

    # Create array to hold a row of data and put timestamp in index 0
    dataRow = np.array([dt])

    # Get Accelerometer data from NI DAQ and append 1000 samples to array
    dataRow = np.append(dataRow, NIDAQ.readVoltage("cDAQ1Mod4", channelNum, 1000, 1000))

    return dataRow

# This function acquires the mic (NI DAQ) data
# and adds it to an array with a timestamp. This array will be written to a csv in the main loop
def acquire_data_mic(channelNum):
    # get current timestamp
    now = datetime.now()
    # current date and time
    dt = now.strftime("%m/%d/%Y, %H:%M:%S.%f")[:-3]

    # Create array to hold a row of data and put timestamp in index 0
    data_list = np.array([dt])

    # Get mic data from NI DAQ and append 20000 samples to array
    data_list = np.append(data_list, NIDAQ.readVoltage("cDAQ1Mod3", channelNum, 40000, 10000))

    return data_list
    #print(data_list)

#creating DataFrame for each mic channel
mic0 = pd.DataFrame()
mic1 = pd.DataFrame()
mic2 = pd.DataFrame()
mic3 = pd.DataFrame()

#creating DataFrame for each accel channel
accel0 = pd.DataFrame(columns=['timestamp','accel0'])
accel1 = pd.DataFrame(columns=['timestamp','accel1'])
#accel2 = pd.DataFrame()

# Set up the Omega object
Omega_Daq = OM_USB_ADC(OM_USB_numb=0)

#creating DataFrames for each load cell
LC0 = pd.DataFrame(columns=['timestamp','lc0'])
LC1 = pd.DataFrame(columns=['timestamp','lc1'])
LC2 = pd.DataFrame(columns=['timestamp','lc2'])
LC3 = pd.DataFrame(columns=['timestamp','lc3'])
LC4 = pd.DataFrame(columns=['timestamp','lc4'])
LC5 = pd.DataFrame(columns=['timestamp','lc5'])
LC6 = pd.DataFrame(columns=['timestamp','lc6'])
LC7 = pd.DataFrame(columns=['timestamp','lc7'])

# Set up the Visa resource for the Tektronix Scope
rm = pyvisa.ResourceManager()
list_dev = rm.list_resources()
Tek_scope = DPO2024B(list_dev[0])

scope = pd.DataFrame(columns=['timestamp','rms'])


#function to record mic data
def record_mic():
#try and catch a keyboard interrupt to end the program
    try:
        #setting the index of the first sample
        column = 0

        while True:
            #add mic data to array
            mic0[str(column)] = acquire_data_mic('ai0').tolist()
            mic0[str(column+1)] = acquire_data_mic('ai1').tolist()
            mic0[str(column+2)] = acquire_data_mic('ai2').tolist()
            mic0[str(column+3)] = acquire_data_mic('ai3').tolist()

            #print(mic0)
            #Change index of mic data sample
            column += 4

            #time.sleep(max(0, t - time.time()))
    except KeyboardInterrupt:
        #write dataframe to csv file at the end of the program when it has been terminated
        mic0.to_csv('mic0.csv')
        #mic1.to_csv('mic1.csv')
        #mic2.to_csv('mic2.csv')
        #mic3.to_csv('mic3.csv')
        print('done')


#function to record mic data
def record_accel0():
    # try and catch a keyboard interrupt to end the program
    try:
        # create the starting index of the array that will be stored in the dataframe
        # sample at 2khz
        period = 0.0005
        t = time.time()
        accel0 = pd.DataFrame(columns=np.arange(1001))

        while True:
            t += period
            # take load cell data sample
            #accel0.loc[len(accel0)] = acquire_data_Accel('ai0')
            new = acquire_data_Accel('ai0')
            accel0 = accel0.append(pd.Series(new, index=accel0.columns[:len(new)]), ignore_index=True)

            time.sleep(max(0, t - time.time()))
            # change the index for the next data sample
    # print to csv file when over
    except KeyboardInterrupt:
        #write dataframe to csv file at the end of the program when it has been terminated
        accel0.to_csv('accel0.csv')
        #accel1.to_csv('accel1.csv')


# function to record Omega Daq - creating one for each specific channel
# todo: get rid of redundancy of calling the same function over and over again
def record_Omega0():
    try:
        # create the starting index of the array that will be stored in the dataframe
        column = 0
        # sample at 2khz
        period = 0.0005
        t = time.time()
        while True:
            t += period
            # take load cell data sample
            LC0.loc[len(LC0)] = acquire_Omega(Omega_Daq, 0)
            time.sleep(max(0, t - time.time()))
            # change the index for the next data sample
            column += 1
    # print to csv file when over
    except KeyboardInterrupt:
        LC0.to_csv('LC0.csv')

#repeating for each channel
def record_Omega1():
    try:
        column = 0
        period = 0.0005
        t = time.time()
        while True:
            t += period
            # LC0.append(acquire_Omega(Omega_Daq, 0))
            LC1.loc[len(LC1)] = acquire_Omega(Omega_Daq, 1)
            # LC0[str(column)] = acquire_Omega(Omega_Daq, 0)
            # print(LC0)
            time.sleep(max(0, t - time.time()))
            column += 1
    except KeyboardInterrupt:
        LC1.to_csv('LC1.csv')
def record_Omega2():
    try:
        column = 0
        period = 0.0005
        t = time.time()
        while True:
            t += period
            # LC0.append(acquire_Omega(Omega_Daq, 0))
            LC2.loc[len(LC2)] = acquire_Omega(Omega_Daq, 1)
            # LC0[str(column)] = acquire_Omega(Omega_Daq, 0)
            # print(LC0)
            time.sleep(max(0, t - time.time()))
            column += 1
    except KeyboardInterrupt:
        LC2.to_csv('LC2.csv')
def record_Omega3():
    try:
        column = 0
        period = 0.0005
        t = time.time()
        while True:
            t += period
            # LC0.append(acquire_Omega(Omega_Daq, 0))
            LC3.loc[len(LC3)] = acquire_Omega(Omega_Daq, 1)
            # LC0[str(column)] = acquire_Omega(Omega_Daq, 0)
            # print(LC0)
            time.sleep(max(0, t - time.time()))
            column += 1
    except KeyboardInterrupt:
        LC3.to_csv('LC3.csv')
def record_Omega4():
    try:
        column = 0
        period = 0.0005
        t = time.time()
        while True:
            t += period
            # LC0.append(acquire_Omega(Omega_Daq, 0))
            LC4.loc[len(LC4)] = acquire_Omega(Omega_Daq, 1)
            # LC0[str(column)] = acquire_Omega(Omega_Daq, 0)
            # print(LC0)
            time.sleep(max(0, t - time.time()))
            column += 1
    except KeyboardInterrupt:
        LC4.to_csv('LC4.csv')
def record_Omega5():
    try:
        column = 0
        period = 0.0005
        t = time.time()
        while True:
            t += period
            # LC0.append(acquire_Omega(Omega_Daq, 0))
            LC5.loc[len(LC5)] = acquire_Omega(Omega_Daq, 1)
            # LC0[str(column)] = acquire_Omega(Omega_Daq, 0)
            # print(LC0)
            time.sleep(max(0, t - time.time()))
            column += 1
    except KeyboardInterrupt:
        LC5.to_csv('LC5.csv')
def record_Omega6():
    try:
        column = 0
        period = 0.0005
        t = time.time()
        while True:
            t += period
            # LC0.append(acquire_Omega(Omega_Daq, 0))
            LC6.loc[len(LC6)] = acquire_Omega(Omega_Daq, 1)
            # LC0[str(column)] = acquire_Omega(Omega_Daq, 0)
            # print(LC0)
            time.sleep(max(0, t - time.time()))
            column += 1
    except KeyboardInterrupt:
        LC6.to_csv('LC6.csv')
def record_Omega7():
    try:
        column = 0
        period = 0.0005
        t = time.time()
        while True:
            t += period
            # LC0.append(acquire_Omega(Omega_Daq, 0))
            LC7.loc[len(LC7)] = acquire_Omega(Omega_Daq, 1)
            # LC0[str(column)] = acquire_Omega(Omega_Daq, 0)
            # print(LC0)
            time.sleep(max(0, t - time.time()))
            column += 1
    except KeyboardInterrupt:
        LC7.to_csv('LC7.csv')

def record_Scope():
    try:
        # create the starting index of the array that will be stored in the dataframe
        column = 0
        # sample at 2khz
        period = 0.0005
        t = time.time()
        while True:
            t += period
            # take load cell data sample
            scope.loc[len(scope)] = acquire_Tek(Tek_scope)
            time.sleep(max(0, t - time.time()))
            # change the index for the next data sample
            column += 1
    # print to csv file when over
    except KeyboardInterrupt:
        scope.to_csv('scope.csv')


if __name__ == "__main__":
    # creating processes
    #p1 = multiprocessing.Process(target=record_mic)
    #p2 = multiprocessing.Process(target=record_accel0)

    # creating processes
    p0 = multiprocessing.Process(target=record_Omega0)
    p1 = multiprocessing.Process(target=record_Omega1)
    p2 = multiprocessing.Process(target=record_Omega2)
    p3 = multiprocessing.Process(target=record_Omega3)
    p4 = multiprocessing.Process(target=record_Omega4)
    p5 = multiprocessing.Process(target=record_Omega5)
    p6 = multiprocessing.Process(target=record_Omega6)
    p7 = multiprocessing.Process(target=record_Omega7)
    p8 = multiprocessing.Process(target=record_mic)
    p9 = multiprocessing.Process(target=record_accel0)
    p10 = multiprocessing.Process(target=record_Scope)

    # starting process
    p0.start()
    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()
    p6.start()
    p7.start()
    p8.start()
    p9.start()
    p10.start()

    # wait until process is finished
    p0.join()
    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()
    p7.join()
    p8.start()
    p9.start()
    p10.start()

    # both processes finished
    print("Done!")