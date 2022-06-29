from csv import writer
from datetime import datetime

import numpy as np
import pyvisa
import threading

from NI_DAQ_Library import NIDAQ
from OMEGA_Library import OM_USB_ADC
from Tektronix_Library import DPO2024B


# Function to acquire Microphone inputs
def NI_DAQ_Mic():
    # Mics are using the 3rd module on our DAQ and there are 4 of them
    arr = np.array([])
    np.append(arr, NIDAQ.readVoltage("cDAQ1Mod3", "Ai0"))
    np.append(arr, NIDAQ.readVoltage("cDAQ1Mod3", "Ai1"))
    np.append(arr, NIDAQ.readVoltage("cDAQ1Mod3", 'Ai2'))
    np.append(arr, NIDAQ.readVoltage("cDAQ1Mod3", 'Ai3'))
    return arr


# This function acquires the Load Cell(Omega Daq), Accelerometer(NI Daq), and Tektronix Scope data
# and adds them to an array with a timestamp. This array will be written to the csv in main loop
def acquire_data(Tek, Omega):
    # get current timestamp
    dt = datetime.now()
    ts = datetime.timestamp(dt)

    # Create array to hold a row of data and put timestamp in index 0
    dataRow = np.array([ts])

    # insert_channel from 0 up to 7
    np.append(dataRow, Omega.voltage_reading(channel=0))
    np.append(dataRow, Omega.voltage_reading(channel=1))
    np.append(dataRow, Omega.voltage_reading(channel=2))
    np.append(dataRow, Omega.voltage_reading(channel=3))
    np.append(dataRow, Omega.voltage_reading(channel=4))
    np.append(dataRow, Omega.voltage_reading(channel=5))
    np.append(dataRow, Omega.voltage_reading(channel=6))
    np.append(dataRow, Omega.voltage_reading(channel=7))

    # Get Accelerometer data from NI DAQ and append to array
    dataRow = np.append(dataRow, NIDAQ.readVoltage("cDAQ1Mod4", "ai0"))
    dataRow = np.append(dataRow, NIDAQ.readVoltage("cDAQ1Mod4", "ai1"))
    dataRow = np.append(dataRow, NIDAQ.readVoltage("cDAQ1Mod4", "ai2"))

    # Get waveform RMS from the scope channel 1 and append to the array
    rms = Tek.waveform_rms(1)
    dataRow = np.append(dataRow, str(rms))

    return dataRow


#  Function used to end the program by taking a keystroke. Called as a separate thread
def task():
    value = input("Press a key to end:\n")
    global log
    log = False
    return


# Main Start. Create the csv writer
with open('event.csv', 'w', newline='') as f_object:
    # Pass this file object to csv.writer()
    # and get a writer object
    writer_object = writer(f_object)

    # Set up the Visa resource for the Tektronix Scope
    rm = pyvisa.ResourceManager()
    list_dev = rm.list_resources()
    Tek_scope = DPO2024B(list_dev[0])

    # Set up the Omega object
    Omega_Daq = OM_USB_ADC(OM_USB_numb=0)

    # Set up the loop and exit variable
    log = True

    #  Run the exit function as a separate thread
    thread = threading.Thread(target=task)
    thread.start()
    # write the header to CSV
    header = ['TS', 'LC1', 'LC2', 'LC3', 'LC4', 'LC5', 'LC6', 'LC7', 'LC8', 'Accel1', 'Accel2', 'Accel3', 'RMS']
    writer_object.writerow(header)
    while log:
        #  Read all inputs and return an array.
        newline = acquire_data(Tek_scope, Omega_Daq)

        # Write the array to a newline in CSV
        writer_object.writerow(newline)

    # Close the file object
    f_object.close()
