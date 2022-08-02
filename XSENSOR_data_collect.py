import ctypes
import XSCore90
import pandas as pd
from datetime import datetime
import warnings
import csv
import numpy as np

# ignore warnings like a real Software Dev
warnings.simplefilter(action='ignore', category=FutureWarning)

# var = XSCore90.XS_GetStreamingMode
# print(var)

# path to save file to
path = r'C:\Users\DanielCooper\Documents\Deck Sense Project\Xsensor Data\XSensor_output.csv'

XSCore90.XS_InitLibrary(1)
# result = XSCore90.XS_InitLibrary(90000)
# print(result)

# pre-define some variables to hold data from the DLL. This is for
sensorPID = 0
sensorIndex = 0
senselRows = ctypes.c_ushort()
senselColumns = ctypes.c_ushort()
senselDimHeight = ctypes.c_float()
senselDimWidth = ctypes.c_float()

sampleYear = ctypes.c_ushort()
sampleMonth = ctypes.c_ubyte()
sampleDay = ctypes.c_ubyte()
sampleHour = ctypes.c_ubyte()
sampleMinute = ctypes.c_ubyte()
sampleSecond = ctypes.c_ubyte()
sampleMillisecond = ctypes.c_ushort()

pressure = ctypes.c_float()  # pressure values only

minPressureRange = ctypes.c_float()
maxPressureRange = ctypes.c_float()

wMajor = ctypes.c_ushort()
wMinor = ctypes.c_ushort()
wBuild = ctypes.c_ushort()
wRevision = ctypes.c_ushort()

nameBufferSize = ctypes.c_uint()

# query the DLL version (for XSENSOR support reference)
XSCore90.XS_GetVersion(ctypes.byref(wMajor), ctypes.byref(wMinor), ctypes.byref(wBuild), ctypes.byref(wRevision))

sVersion = 'DLL Version ' + str(wMajor.value) + '.' + repr(wMinor.value) + ' build ' + str(wBuild.value) + '\n'
print(sVersion)

# Set a calibration cache folder. The DLL will download calibration files from the sensor and
# place them in this folder. This will speed up enumeration on subsequent calls.
# This call is optional, but recommended. You must also supply a valid path, or more specifically
# a path with WRITE permissions.

XSCore90.XS_SetCalibrationFolder("e:\CalCache")

# Tell the DLL to find any wired (USB) X4 sensors - only do this if you are using wired - slow otherwise)
# 1 = true, 0 = false
# XSCore90.XS_SetAllowX4(1);

# Tell the DLL to find any Bluetooth X4 sensors - only do this if you are using Bluetooth - slow otherwise)
XSCore90.XS_SetAllowX4Wireless(1);

# Tell the DLL use 8 bit mode for X4.  This can improve the reliability of Bluetooth transmission speeds. Has no impact on actual recording speed.
XSCore90.XS_SetX4Mode8Bit(1);

# Use streaming mode if you are retrieving frames as fast as the sensor can deliver them.
# Set streaming mode off (0) if you are asking for frames at a rate lower than the sampling rate
XSCore90.XS_SetStreamingMode(1);

b = ctypes.c_ubyte()
b = XSCore90.XS_GetStreamingMode()
print(b)

# XSCore90.XS_SetAllowFastEnum(1);

# Ask the DLL to scan the computer for attached sensors. Returns the number of sensors found.
nbrSensors = XSCore90.XS_EnumSensors()

# Fetch last enum state. Examine this if no sensors are found. Look up EEnumerationError in XSCore90.py
# The returned value might have a combination of the bits set from EEnumerationError.
lastEnumState = XSCore90.XS_GetLastEnumState()

sMesg = 'Found ' + str(nbrSensors) + ' sensors; ' + 'Last Enumeration State: ' + str(lastEnumState) + '\n'
print(sMesg)

# creating time stamp for when test started
now = datetime.now()
date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

# log file header
file_version = ['LogFileVersion:', 'v1.0']
name = ['NAME:', 'X_Sensor Data Logger']
value = ['DESCRIPTION:', 'Raw Sensel']
date_of_acquisition = ['DATE:', date_time_str]
newline = ['']

# create header in log file
with open(path, 'a', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(file_version)
    writer.writerow(name)
    writer.writerow(value)
    writer.writerow(date_of_acquisition)
    writer.writerow(newline)


def write_to_csv(junk):
    junk_writer = [junk]
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(junk_writer)


cpath = r'C:\Users\DanielCooper\Documents\Deck Sense Project\Xsensor Data\XSensor_output.xsn'
c_cpath = cpath.encode('utf-8')

# Build a sensor configuration. The DLL must be told which sensors to use.
if nbrSensors > 0:
    sMesg = 'Building sensor configuration...'
    print(sMesg)
    nbrSensors = 0

    # This will automatically configure all sensors on the computer
    if XSCore90.XS_AutoConfigByDefaultXSN(c_cpath) == 1:
        nbrSensors = XSCore90.XS_ConfigSensorCount()
        sMesg = 'Configured ' + str(nbrSensors) + ' sensors\n'
        print(sMesg)

# Tell the DLL we want all pressure values in the following units
XSCore90.XS_SetPressureUnit(ctypes.c_ubyte(XSCore90.EPressureUnit.ePRESUNIT_KGCM2.value))

# Inspect the configured sensor(s) - this is for reference only
while sensorIndex < nbrSensors:
    # fetch the sensors product ID - this is needed by some functions
    sensorPID = XSCore90.XS_ConfigSensorPID(sensorIndex)

    # fetch the sensor serial number. This is for reference only
    serialNbr = XSCore90.XS_GetSerialFromPID(sensorPID)

    # determine how many rows and columns this sensor has
    XSCore90.XS_GetSensorDimensions(sensorPID, ctypes.byref(senselRows), ctypes.byref(senselColumns))

    # determine the measurement dimensions of a single sensor cell (called a Sensel)
    XSCore90.XS_GetSenselDims(sensorPID, ctypes.byref(senselDimWidth), ctypes.byref(senselDimHeight))

    # fetch the sensor name - first get the string buffer size
    XSCore90.XS_GetSensorName(sensorPID, ctypes.byref(nameBufferSize), None)

    # construct a buffer for the name
    # sName = ctypes.create_unicode_buffer(nameBufferSize.value)
    sName = (ctypes.c_wchar * (nameBufferSize.value))()

    # retrieve the name
    XSCore90.XS_GetSensorName(sensorPID, ctypes.byref(nameBufferSize), ctypes.byref(sName))

    sMesg = '\tSensor Info PID ' + str(sensorPID) + '; Serial S' + str(serialNbr) + '; [' + sName.value + ']'
    write_to_csv(sMesg)
    print(sMesg)
    sMesg = '\tRows ' + str(senselRows.value) + '; Columns ' + str(senselColumns.value)
    write_to_csv(sMesg)
    print(sMesg)
    sMesg = '\tWidth(cm) {:0.3f}'.format(
        float(senselColumns.value) * senselDimWidth.value) + '; Height(cm) {:0.3f}'.format(
        float(senselRows.value) * senselDimHeight.value) + '\n'
    write_to_csv(sMesg)
    print(sMesg)

    # fetch the current calibration range of the sensor (calibrated min/max pressures)
    XSCore90.XS_GetConfigInfo(ctypes.c_ubyte(XSCore90.EPressureUnit.ePRESUNIT_KGCM2.value),
                              ctypes.byref(minPressureRange), ctypes.byref(maxPressureRange))

    sMesg = '\tMin pressure {:0.4f} '.format(float(minPressureRange.value)) + str(
        XSCore90.EPressureUnit.ePRESUNIT_KGCM2) + ' Max pressure {:0.4f} '.format(float(maxPressureRange.value)) + str(
        XSCore90.EPressureUnit.ePRESUNIT_KGCM2)
    write_to_csv(sMesg)
    print(sMesg)

    write_to_csv('')

    sensorIndex = sensorIndex + 1

# Okay time to retrieve some frames of data

# before opening the connection, set a frame rate. Its in terms of frames per minute. So a 100 Hz rate means (100 x 60 => 6000 frames per minute)

# buffer variable
data_buff = []
data_out = pd.DataFrame()
data_out2 = pd.DataFrame()

# Open a connection to the configured sensor(s) - we'll ask for 100 Hz or 6000 frames per minute
if XSCore90.XS_OpenConnection(12000) == 1:

    # print(XSCore90.XS_GetStreamingMode)

    try:
        # continuous data logger - this will only end with a keyboard interrupt
        while True:
            sMesg = '\nRequesting Sample...'
            print(sMesg)

            # request the sample - this call blocks until the samples are buffered
            if XSCore90.XS_Sample() == 1:

                # fetch the sample timestamp
                XSCore90.XS_GetSampleTimestampUTC(ctypes.byref(sampleYear), ctypes.byref(sampleMonth),
                                                  ctypes.byref(sampleDay), ctypes.byref(sampleHour),
                                                  ctypes.byref(sampleMinute), ctypes.byref(sampleSecond),
                                                  ctypes.byref(sampleMillisecond))

                timestamp_msg = '{:02d}'.format(sampleHour.value - 7) + ':{:02d}'.format(
                    sampleMinute.value) + ':{:02d}'.format(sampleSecond.value) + '.{:03d}'.format(
                    sampleMillisecond.value)

                """
                timestamp_msg = 'Timestamp: ' + str(sampleYear.value) + '-{:02d}'.format(sampleMonth.value) + '-{:02d}'.format(
                    sampleDay.value) + 'T{:02d}'.format(sampleHour.value) + ':{:02d}'.format(
                    sampleMinute.value) + ':{:02d}'.format(sampleSecond.value) + '.{:03d}'.format(sampleMillisecond.value)
                """
                # print(timestamp_msg)

                # each configured sensor has its own frame buffer
                sensorIndex = 0
                while sensorIndex < nbrSensors:

                    # fetch the sensor Product ID (PID)
                    sensorPID = XSCore90.XS_ConfigSensorPID(sensorIndex)
                    sensorIndex = sensorIndex + 1

                    # convert to datetime
                    final_time = datetime.strptime(timestamp_msg, '%H:%M:%S.%f')

                    # convert timestamp to seconds
                    a_timedelta = final_time - datetime(1900, 1, 1)
                    timestamp_seconds = a_timedelta.total_seconds()

                    # create timestamp and PID in csv file
                    data_out[('Time_Stamp')] = timestamp_seconds

                    # get sensor ID and assign LEFT(foot) or RIGHT(foot) based on the ID #
                    modPID = sensorPID % 1000
                    # if it ends with 425 then it is the LEFT foot
                    if modPID == 425:
                        data_out[('ID')] = 'LEFT'
                    # if it ends with 681 then it is the RIGHT foot
                    elif modPID == 681:
                        data_out[('ID')] = 'RIGHT'

                    # data_out[('PID')] = modPID

                    # need the sensor dimensions to pre-allocate some buffer space
                    XSCore90.XS_GetSensorDimensions(sensorPID, ctypes.byref(senselRows), ctypes.byref(senselColumns))

                    # construct a frame buffer for this sensor
                    frameBuffer = (ctypes.c_float * (senselRows.value * senselColumns.value))()

                    print('Calling XS_GetPressure')

                    # retrieve the recorded frame
                    if XSCore90.XS_GetPressure(sensorPID, ctypes.byref(frameBuffer)) == 1:

                        print('Got pressure frame')
                        print(sensorPID)

                        # now dump the frame to the console window
                        for row in range(senselRows.value):
                            for column in range(senselColumns.value):
                                # take pressure reading
                                pressure.value = frameBuffer[row * senselColumns.value + column]
                                sMesg = '{:0.2f}, '.format(pressure.value)
                                print(sMesg, end='')

                                # save pressure into an array
                                data_buff.append(pressure.value)

                            print('')  # line break for end of row
                            # place array in the dataframe
                            data_out[('col ' + str(row))] = data_buff
                            # reset array
                            data_buff = []

                        # append data frame into an empty data frame
                        # this removes the repeating headers
                        data_out2 = data_out2.append(data_out)

    # stop the while loop with a keyboard press
    except KeyboardInterrupt:
        # remove any data that does not have a timestamp
        data_out2['Time_Stamp'].replace('', np.nan, inplace=True)
        data_out2.dropna(subset=['Time_Stamp'], inplace=True)

        # convert dataframe into a csv file
        data_out2.to_csv(path, mode='ab', index=False)
        # close the connection
        XSCore90.XS_CloseConnection()

# call ExitLibrary to free any resources used by the DLL
XSCore90.XS_ExitLibrary()
