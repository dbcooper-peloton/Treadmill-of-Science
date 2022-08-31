import ctypes
import XSCore90
import XSNReader
import pandas as pd
from datetime import datetime
import warnings
import csv
import numpy as np

# csv file path
path = r"C:\TOS_Data\XSensor\XSensor_output.csv"
# XSN file path
path2 = r"C:\TOS_Data\XSensor\X_log.XSN"
# calibration file path
path3 = r"C:\Users\preco\OneDrive\Desktop\Project-Orchid\XSensor\ToS\Calibration"

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

XSCore90.XS_InitLibrary(1)
# query the DLL version (for XSENSOR support reference)
XSCore90.XS_GetVersion(ctypes.byref(wMajor), ctypes.byref(wMinor), ctypes.byref(wBuild), ctypes.byref(wRevision))

sVersion = 'DLL Version ' + str(wMajor.value) + '.' + repr(wMinor.value) + ' build ' + str(wBuild.value) + '\n'
print(sVersion)

# Need cali folder
XSCore90.XS_SetCalibrationFolder(path3)

# Tell the DLL to find any Bluetooth X4 sensors - only do this if you are using Bluetooth - slow otherwise)
XSCore90.XS_SetAllowX4Wireless(1);
XSCore90.XS_SetX4Mode8Bit(1);
XSCore90.XS_SetStreamingMode(1);

# Ask the DLL to scan the computer for attached sensors. Returns the number of sensors found.
nbrSensors = XSCore90.XS_EnumSensors()
lastEnumState = XSCore90.XS_GetLastEnumState()
sMesg = 'Found ' + str(nbrSensors) + ' sensors; ' + 'Last Enumeration State: ' + str(lastEnumState) + '\n'
print(sMesg)

# creating time stamp for when test started
now = datetime.now()
date_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

# Use this to write header and other non-frame info to the csv
def write_to_csv(junk):
    junk_writer = [junk]
    with open(path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(junk_writer)


# Use this post acquisition to read from the XSN log and write to CSV
def XSN_to_CSV():
    XSNReader.XSN_InitLibrary()
    # query the DLL version (for XSENSOR support reference)
    xwMajor = XSNReader.XSN_GetLibraryMajorVersion()
    xwMinor = XSNReader.XSN_GetLibraryMinorVersion()

    # buffer variables
    data_buff = []
    data_out = pd.DataFrame()
    data_out2 = pd.DataFrame()

    sVersion = 'DLL Version ' + str(wMajor) + '.' + str(wMinor) + '\n'
    print(sVersion)

    if XSNReader.XSN_LoadSessionU(path2):
        # fetch information about the session and write to csv
        sMesg = 'Session contains ' + str(XSNReader.XSN_FrameCount()) + ' frames'
        # write_to_csv(sMesg)
        sMesg = 'Session contains ' + str(XSNReader.XSN_PadCount()) + ' pads'
        # write_to_csv(sMesg)

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
            # write_to_csv(sMesg)

            padWidth = widthCM.value * float(XSNReader.XSN_Columns(pad))
            padHeight = heightCM.value * float(XSNReader.XSN_Rows(pad))

            sMesg = 'Pad dims: {:0.3f}'.format(padWidth) + 'cm width x {:0.3f}'.format(padHeight) + 'cm length\n'
            # write_to_csv(sMesg)

        sMesg = 'XSN pressure units is ' + str(XSNReader.XSN_GetPressureUnits())
        write_to_csv(sMesg)

        frameCount = XSNReader.XSN_FrameCount()
        frame = 1
        # !!!! Main loop!!! process every frame from the XSN file and write them to csv
        while frame <= frameCount:

            sMesg = '\nStep to Frame ' + str(frame)
            print(sMesg)

            # Step to the frame
            if XSNReader.XSN_StepToFrame(frame) == 0:
                sMesg = 'Step to Frame failed'
                print(sMesg)

            frameID = XSNReader.XSN_GetFrameID()

            sMesg = 'Processing Frame ID ' + str(frameID)
            print(sMesg)

            # Get frame timestamp and write csv
            XSNReader.XSN_GetTimeStampUTC(ctypes.byref(nYear), ctypes.byref(nMonth), ctypes.byref(nDay),
                                          ctypes.byref(nHour), ctypes.byref(nMinute), ctypes.byref(nSecond),
                                          ctypes.byref(nMilliseconds))
            timestamp_msg = '{:02d}'.format(nHour.value - 7) + ':{:02d}'.format(
                nMinute.value) + ':{:02d}'.format(nSecond.value) + '.{:03d}'.format(
                nMilliseconds.value)

            for pad in range(padCount):

                # convert
                # to
                # datetime
                final_time = datetime.strptime(timestamp_msg, '%H:%M:%S.%f')

                # convert timestamp to seconds
                a_timedelta = final_time - datetime(1900, 1, 1)
                timestamp_seconds = a_timedelta.total_seconds()

                # create timestamp and PID in csv file
                data_out['Time_Stamp'] = timestamp_seconds

                # get sensor ID and assign LEFT(foot) or RIGHT(foot) based on the ID #
                XSNReader.XSN_GetPadInfoEx(pad, None, ctypes.byref(nModelLength), None, ctypes.byref(nProductLength),
                                           None,
                                           ctypes.byref(nSerialLength))

                # construct string buffers
                sModel = (ctypes.c_wchar * (nModelLength.value))()
                sProductID = (ctypes.c_wchar * (nProductLength.value))()
                sSerial = (ctypes.c_wchar * (nSerialLength.value))()

                # retrieve the strings
                XSNReader.XSN_GetPadInfoEx(pad, ctypes.byref(sModel), ctypes.byref(nModelLength),
                                           ctypes.byref(sProductID),
                                           ctypes.byref(nProductLength), ctypes.byref(sSerial),
                                           ctypes.byref(nSerialLength))

                # determine the measurement dimensions of a single sensor cell (called a Sensel)
                XSNReader.XSN_GetPadSenselDims(pad, ctypes.byref(widthCM), ctypes.byref(heightCM))

                # modPID = sProductID.value % 1000
                data_out['ID'] = sModel.value[-2]


                senselColumns = XSNReader.XSN_Columns(pad);
                senselRows = XSNReader.XSN_Rows(pad);

                # construct a frame buffer for this sensor .. should probably cache this?
                frameBuffer = (ctypes.c_float * (XSNReader.XSN_Columns(pad) * XSNReader.XSN_Rows(pad)))()

                if XSNReader.XSN_GetPressureMapEx(pad, ctypes.byref(frameBuffer), ctypes.byref(frameBufferSize)) == 1:
                    print('Got pressure frame')

                    # now dump the frame to the console window
                    for row in range(senselRows):
                        for column in range(senselColumns):
                            pressure.value = frameBuffer[row * senselColumns + column]
                            sMesg = '{:0.2f}, '.format(pressure.value)
                            print(sMesg, end='')
                            # save pressure into an array
                            data_buff.append(pressure.value)

                        print('')  # line break for end of row
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


# Build a sensor configuration. The DLL must be told which sensors to use.
if nbrSensors > 0:
    sMesg = 'Building sensor configuration...'
    print(sMesg)
    nbrSensors = 0

    # This will automatically configure all sensors on the computer
    # set unit of measurement

    # pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_MMHG.value # millimeters of mercury
    # pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_INH2O.value # inches of water
    pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_PSI.value  # pounds/sq.inch
    # pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_KPA.value # kilopascals
    # pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_KGCM2.value # kgf/cm^2
    # pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_ATM.value # atmospheres
    # pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_NCM2.value # newtons/cm^2
    # pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_MBAR.value # millibars
    # pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_NM2.value # Newton/meter^2
    # pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_GCM2.value # grams/cm^2
    # pressure_unit = XSCore90.EPressureUnit.ePRESUNIT_RAW.value # non-calibrated readings from the sensors - 16 bit integers


    if XSCore90.XS_AutoConfigXSN(path2, pressure_unit, -1.0) == 1:
        nbrSensors = XSCore90.XS_ConfigSensorCount()
        sMesg = 'Configured ' + str(nbrSensors) + ' sensors\n'
        print(sMesg)

# Tell the DLL we want all pressure values in the following units
XSCore90.XS_SetPressureUnit(ctypes.c_ubyte(pressure_unit))
print(str(XSCore90.XS_GetPressureUnit()))

# Inspect the configured sensor(s) - then write sensor info to file
while sensorIndex < nbrSensors:
    # Get Sensor info
    sensorPID = XSCore90.XS_ConfigSensorPID(sensorIndex)
    serialNbr = XSCore90.XS_GetSerialFromPID(sensorPID)
    XSCore90.XS_GetSensorDimensions(sensorPID, ctypes.byref(senselRows), ctypes.byref(senselColumns))
    XSCore90.XS_GetSenselDims(sensorPID, ctypes.byref(senselDimWidth), ctypes.byref(senselDimHeight))
    XSCore90.XS_GetSensorName(sensorPID, ctypes.byref(nameBufferSize), None)

    # construct a buffer for the name
    # sName = ctypes.create_unicode_buffer(nameBufferSize.value)
    sName = (ctypes.c_wchar * (nameBufferSize.value))()

    # retrieve the name
    XSCore90.XS_GetSensorName(sensorPID, ctypes.byref(nameBufferSize), ctypes.byref(sName))

    # sMesg = '\tSensor Info PID ' + str(sensorPID) + '; Serial S' + str(serialNbr) + '; [' + sName.value + ']'
    # write_to_csv(sMesg)

    if sensorIndex == 0:
        # Write some sensor info to the CSV header
        # sMesg = '\tRows ' + str(senselRows.value) + '; Columns ' + str(senselColumns.value)
        # write_to_csv(sMesg)
        sMesg = ['DIMENSIONS:', 'Width(cm)', '{:0.3f}'.format(
            float(senselColumns.value) * senselDimWidth.value), 'Height(cm)', '{:0.3f}'.format(
            float(senselRows.value) * senselDimHeight.value)]

        # checking what the units of measurements is in the XSN file
        if str(XSCore90.XS_GetPressureUnit()) == '2':
            sMesg = 'PSI'
        else:
            sMesg = 'ERROR not in PSI'


        # log file header
        file_version = ['LogFileVersion:', 'v1.0']
        name = ['NAME:', 'X_Sensor Data Logger']
        value = ['DESCRIPTION:', str(sMesg)]
        date_of_acquisition = ['DATE:', date_time_str]
        newline = [' ']

        # create header in log file
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(file_version)
            writer.writerow(name)
            writer.writerow(value)
            writer.writerow(date_of_acquisition)
            writer.writerow(newline)
    # fetch the current calibration range of the sensor (calibrated min/max pressures)
    XSCore90.XS_GetConfigInfo(ctypes.c_ubyte(pressure_unit),
                              ctypes.byref(minPressureRange), ctypes.byref(maxPressureRange))

    sMesg = '\tMin pressure {:0.4f} '.format(float(minPressureRange.value)) + str(
        XSCore90.EPressureUnit.ePRESUNIT_PSI) + ' Max pressure {:0.4f} '.format(
        float(maxPressureRange.value)) + str(
        XSCore90.EPressureUnit.ePRESUNIT_PSI)
    write_to_csv(sMesg)
    print(sMesg)
    sensorIndex = sensorIndex + 1

# buffer variables - do we need all of these?
data_buff = []
data_out = pd.DataFrame()
data_out2 = pd.DataFrame()

# !!!!Main acquisition loop - Open connection with desired frames per minute
if XSCore90.XS_OpenConnection(9000) == 1:
    try:
        # continuous data logger - this will only end with a keyboard interrupt
        sMesg = '\nLogging'
        while True:
            print(sMesg)
    # stop the while loop with a keyboard press
    except KeyboardInterrupt:
        XSCore90.XS_CloseConnection()
        XSCore90.XS_ExitLibrary()
        XSN_to_CSV()
