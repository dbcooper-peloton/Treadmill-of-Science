import ctypes
import XSNReader
import pandas as pd
from datetime import datetime
import warnings
import csv
import numpy as np

warnings.simplefilter(action='ignore', category=FutureWarning)
# pre-define some variables to hold data from XCore90 DLL

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

# pre-define some variables to hold data from XSNReader DLL
heightCM = ctypes.c_float()
widthCM = ctypes.c_float()
padCount = ctypes.c_ubyte()

xwMajor = ctypes.c_ushort()
xwMinor = ctypes.c_ushort()

nModelLength = ctypes.c_uint()
nProductLength = ctypes.c_uint()
nSerialLength = ctypes.c_uint()

frame = ctypes.c_uint()
frameID = ctypes.c_uint()

nYear = ctypes.c_ushort()
nMonth = ctypes.c_ushort()
nDay = ctypes.c_ushort()
nHour = ctypes.c_ushort()
nMinute = ctypes.c_ushort()
nSecond = ctypes.c_ushort()
nMilliseconds = ctypes.c_ushort()

frameBufferSize = ctypes.c_uint()


path = r'C:\Users\DanielCooper\Documents\Deck Sense Project\Xsensor Data\XSensor_output.csv'


# Use this to write header and other non-frame info to the csv
def write_to_csv(junk):
    junk_writer = [junk]
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(junk_writer)


result = XSNReader.XSN_InitLibrary()
print(result)
# query the DLL version (for XSENSOR support reference)
xwMajor = XSNReader.XSN_GetLibraryMajorVersion()
xwMinor = XSNReader.XSN_GetLibraryMinorVersion()

# buffer variables
data_buff = []
data_out = pd.DataFrame()
data_out2 = pd.DataFrame()

sVersion = 'DLL Version ' + str(xwMajor) + '.' + str(xwMinor) + '\n'
print(sVersion)

if XSNReader.XSN_LoadSessionU(r"C:\Users\DanielCooper\Documents\Deck Sense Project\Xsensor Data\X_log.XSN"):
    # fetch information about the session and write to csv
    sMesg = 'Session contains ' + str(XSNReader.XSN_FrameCount()) + ' frames'
    write_to_csv(sMesg)
    sMesg = 'Session contains ' + str(XSNReader.XSN_PadCount()) + ' pads'
    write_to_csv(sMesg)

    # This gets sensor and session info and writes it to csv - may not need this
    padCount = XSNReader.XSN_PadCount()
    for pad in range(padCount):
        # bool XSN_GetPadInfoEx(uint8_t pad, wchar_t* sModel, uint32_t& nModelLength, wchar_t* sProductID, uint32_t& nProductLength, wchar_t* sSerial, uint32_t& nSerialLength);
        # fetch the sensor name - first get the string buffer size
        XSNReader.XSN_GetPadInfoEx(pad, None, ctypes.byref(nModelLength), None, ctypes.byref(nProductLength), None,
                                   ctypes.byref(nSerialLength))

        # construct string buffers
        sModel = (ctypes.c_wchar * (nModelLength.value))()
        sProductID = (ctypes.c_wchar * (nProductLength.value))()
        sSerial = (ctypes.c_wchar * (nSerialLength.value))()

        # retrieve the strings
        XSNReader.XSN_GetPadInfoEx(pad, ctypes.byref(sModel), ctypes.byref(nModelLength), ctypes.byref(sProductID),
                                   ctypes.byref(nProductLength), ctypes.byref(sSerial), ctypes.byref(nSerialLength))

        # determine the measurement dimensions of a single sensor cell (called a Sensel)
        XSNReader.XSN_GetPadSenselDims(pad, ctypes.byref(widthCM), ctypes.byref(heightCM))

        sMesg = 'Pad' + str(
            pad) + '[' + sModel.value + ' ' + sProductID.value + ' ' + sSerial.value + '] has ' + str(
            XSNReader.XSN_Rows(pad)) + ' rows; ' + str(XSNReader.XSN_Columns(pad)) + ' columns.'
        write_to_csv(sMesg)

        padWidth = widthCM.value * float(XSNReader.XSN_Columns(pad))
        padHeight = heightCM.value * float(XSNReader.XSN_Rows(pad))

        sMesg = 'Pad dims: {:0.3f}'.format(padWidth) + 'cm width x {:0.3f}'.format(padHeight) + 'cm length\n'
        write_to_csv(sMesg)

    sMesg = 'Session base pressure units is ' + str(XSNReader.XSN_GetPressureUnits())
    write_to_csv(sMesg)
    XSNReader.XSN_SetPressureUnits(XSNReader.EXSNPressureUnit.eXSNPRESUNIT_KGCM2.value);

    frameCount = XSNReader.XSN_FrameCount()
    frame = 1
    # !!!! Main loop!!! process every frame from the XSN file and write them to csv
    while frame <= frameCount:

        # sMesg = '\nStep to Frame ' + str(frame)
        # print(sMesg)

        # Step to the frame
        if XSNReader.XSN_StepToFrame(frame) == 0:
            sMesg = 'Step to Frame failed'
            print(sMesg)

        # frameID = XSNReader.XSN_GetFrameID()
        #
        # sMesg = 'Processing Frame ID ' + str(frameID)
        # print(sMesg)

        # Get frame timestamp and write csv
        XSNReader.XSN_GetTimeStampUTC(ctypes.byref(nYear), ctypes.byref(nMonth), ctypes.byref(nDay),
                                      ctypes.byref(nHour), ctypes.byref(nMinute), ctypes.byref(nSecond),
                                      ctypes.byref(nMilliseconds))
        timestamp_msg = '{:02d}'.format(nHour.value - 7) + ':{:02d}'.format(
            nMinute.value) + ':{:02d}'.format(nSecond.value) + '.{:03d}'.format(
            nMilliseconds.value)

        # convert to datetime
        final_time = datetime.strptime(timestamp_msg, '%H:%M:%S.%f')

        # convert timestamp to seconds
        a_timedelta = final_time - datetime(1900, 1, 1)
        timestamp_seconds = a_timedelta.total_seconds()

        for pad in range(padCount):
            # create timestamp and PID in csv file
            data_out['Time_Stamp'] = timestamp_seconds

            # get sensor ID and assign LEFT(foot) or RIGHT(foot) based on the ID #

            modPID = sensorPID % 1000
            data_out['ID'] = modPID

            senselColumns = XSNReader.XSN_Columns(pad);
            senselRows = XSNReader.XSN_Rows(pad);

            # construct a frame buffer for this sensor .. should probably cache this?
            frameBuffer = (ctypes.c_float * (XSNReader.XSN_Columns(pad) * XSNReader.XSN_Rows(pad)))()
            #dataBuffer = np.empty(senselRows, senselColumns)


            if XSNReader.XSN_GetPressureMapEx(pad, ctypes.byref(frameBuffer), ctypes.byref(frameBufferSize)) == 1:
                #print('Got pressure frame')

                #dataBuffer =
                # now dump the frame to the console window
                for row in range(senselRows):
                    for column in range(senselColumns):
                        pressure.value = frameBuffer[row * senselColumns + column]
                        sMesg = '{:0.2f}, '.format(pressure.value)
                        print(sMesg, end='')
                        # save pressure into an array
                        data_buff.append(pressure.value)

                    # print('')  # line break for end of row
                    # place array in the dataframe and flush
                    data_out[('col ' + str(row))] = data_buff
                    data_buff = []

                # append data frame into an empty data frame which removes repeating headers. Why though? think we can cut this buffer if we fix the repeating headers
                data_out2 = data_out2.append(data_out)
        frame += 1

    # remove any data that does not have a timestamp
    data_out2['Time_Stamp'].replace('', np.nan, inplace=True)
    data_out2.dropna(subset=['Time_Stamp'], inplace=True)

    # convert dataframe into a csv file
    data_out2.to_csv(path, mode='ab', index=False)
    XSNReader.XSN_CloseSession()

# call ExitLibrary to free any resources used by the DLL
XSNReader.XSN_ExitLibrary()
