# ===========================================================================
# Demonstration of Python 3.6 wrapper for the XSCore90 DLL (32 or 64 bits)
# Implemented as per https://docs.python.org/3/library/ctypes.html
#
# Copyright (C) 2010-2022  XSENSOR Technology Corporation. All rights reserved.
# ===========================================================================
# This file demonstrates sensor enumeration; auto-configuration and
# retrieving a pressure frame from one or more sensors.
# ===========================================================================

import time
import ctypes
import XSCore90

# C++ programmer note: the import XSCore90 imports the wrapper script and runs it.

# ===========================================================================
# Demo Usage
#
# This file demonstrates how to use the Python DLL wrapper to retrieve
# pressure frames from an XSENSOR pressure sensor.
# ===========================================================================

# Initialize the DLL library
# - pass in 1 for threaded mode, and 0 otherwise
result = XSCore90.XS_InitLibrary(1)

# pre-define some variables to hold data from the DLL.
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

prevsampleMinute = ctypes.c_ubyte()
prevsampleSecond = ctypes.c_ubyte()
prevsampleMillisecond = ctypes.c_ushort()

pressureUnits = ctypes.c_ubyte()

# IMU test
qx = ctypes.c_float()
qy = ctypes.c_float()
qz = ctypes.c_float()
qw = ctypes.c_float()
ax = ctypes.c_float()
ay = ctypes.c_float()
az = ctypes.c_float()
gx = ctypes.c_float()
gy = ctypes.c_float()
gz = ctypes.c_float()

# hardware frame state
hwSequence = ctypes.c_uint()
hwTicks = ctypes.c_uint()

pressure = ctypes.c_float() # pressure values only

minPressureRange = ctypes.c_float()
maxPressureRange = ctypes.c_float()

wMajor = ctypes.c_ushort()
wMinor = ctypes.c_ushort()
wBuild = ctypes.c_ushort()
wRevision = ctypes.c_ushort()

nameBufferSize = ctypes.c_uint()

# query the DLL version (for XSENSOR support reference)
XSCore90.XS_GetVersion(ctypes.byref(wMajor), ctypes.byref(wMinor), ctypes.byref(wRevision), ctypes.byref(wBuild))

sVersion = 'DLL Version: ' + str(wMajor.value) + '.' + repr(wMinor.value) + '.' + repr(wRevision.value) + '.' + repr(wBuild.value) + '\n'
print (sVersion)

# Set a calibration cache folder. The DLL will download calibration files from the sensor and
# place them in this folder. This will speed up enumeration on subsequent calls.
# This call is optional, but recommended. You must also supply a valid path, or more specifically
# a path with WRITE permissions.

sCalCacheFolder = "e:\CalCache"
XSCore90.XS_SetCalibrationFolderUTF8(sCalCacheFolder.encode('utf-8'))
# XSCore90.XS_SetCalibrationFolder(sCalCacheFolder)


framesPerMinute = 10 * 60	# 10 Hz or 600 frames per minute

enableIMU = False
allowX4 = True
wirelessX4 = False

if allowX4:
	if wirelessX4:
		XSCore90.XS_SetAllowX4Wireless(1)

	# Use the following call with xTRUE if you are connecting to the sensors over USB wire
	if not wirelessX4:
		XSCore90.XS_SetAllowX4(1)
	# If you use BOTH XS_SetAllowX4Wireless(xTRUE) and XS_SetAllowX4(xTRUE) at the same time, the DLL will favour USB wired over wireless.

	# Use 8 bit mode when transmitting over Bluetooth wireless to ensure higher framerates
	if wirelessX4:
		XSCore90.XS_SetX4Mode8Bit(1)

	XSCore90.XS_SetSampleAverageCount(4) # 4 or 8 for X4 sensors. smaller number is faster, but with slightly worse signal-to-noise

	framesPerMinute = 75 * 60; # 75 Hz

	# if you're testing X4 insole sensor, you can use this
	if enableIMU:
		XSCore90.XS_SetEnableIMU(1) # if we want IMU data with each frame

else:
	enableIMU = False; # not supported by X3

	# 1, 2, 4, 8 for X3 sensors. smaller number is faster, but with slightly worse signal-to-noise
	XSCore90.XS_SetSampleAverageCount(1)


sMesg = "Enumerating sensors and configuring...\n"
print (sMesg)

# Ask the DLL to scan the computer for attached sensors. Returns the number of sensors found.
nbrSensors = XSCore90.XS_EnumSensors()

# Fetch last enum state. Examine this if no sensors are found. Look up EEnumerationError in XSCore90.py
# The returned value might have a combination of the bits set from EEnumerationError.
lastEnumState = XSCore90.XS_GetLastEnumState()

sMesg = 'Found ' + str(nbrSensors) + ' sensors; ' + 'Last Enumeration State: ' + str(lastEnumState) + '\n'
print (sMesg)

# Build a sensor configuration. The DLL must be told which sensors to use.
if nbrSensors > 0:
	sMesg = 'Building sensor configuration...'
	print (sMesg)
	nbrSensors = 0
	
	# This will automatically configure all sensors on the computer
	if XSCore90.XS_AutoConfigByDefault() == 1:
	
		nbrSensors = XSCore90.XS_ConfigSensorCount()
		sMesg = 'Configured ' + str(nbrSensors) + ' sensors\n'
		print (sMesg)

		# XS_AutoConfigByDefault() changes the pressure units to the default calibration units.
		# We must set the desired pressure units after this call is made
		sPressureUnits = str(XSCore90.EPressureUnit.ePRESUNIT_PSI)
		pressureUnits = ctypes.c_ubyte(XSCore90.EPressureUnit.ePRESUNIT_PSI.value)
		XSCore90.XS_SetPressureUnit(ctypes.c_ubyte(XSCore90.EPressureUnit.ePRESUNIT_PSI.value))

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

	# fetch the buffer size for the sensor name buffer
	XSCore90.XS_GetSensorNameUTF8(sensorPID, ctypes.byref(nameBufferSize), None)
	
	# construct a buffer for the name
	nameBuff =  (ctypes.c_char*(nameBufferSize.value))()

	# retrieve the name as a UTF8 string
	XSCore90.XS_GetSensorNameUTF8(sensorPID, ctypes.byref(nameBufferSize), ctypes.byref(nameBuff))
	sensorName = str(nameBuff.value.decode('utf-8'))

	# an alternate to using UTF8 is to use the Unicode 16 (wchar_t) calls
	# XSCore90.XS_GetSensorName(sensorPID, ctypes.byref(nameBufferSize), None)
	# nameBuff =  (ctypes.c_wchar*(nameBufferSize.value))()
	# XSCore90.XS_GetSensorName(sensorPID, ctypes.byref(nameBufferSize), ctypes.byref(nameBuff))
	# sensorName = str(nameBuff.value)

	sMesg = '\tSensor Info PID ' + str(sensorPID) + '; Serial S' + str(serialNbr) + '; [' + sensorName + ']'
	print (sMesg)
	sMesg = '\tRows ' + str(senselRows.value) + '; Columns ' + str(senselColumns.value)
	print (sMesg)
	sMesg = '\tWidth(cm) {:0.3f}'.format(float(senselColumns.value) * senselDimWidth.value) + '; Height(cm) {:0.3f}'.format(float(senselRows.value) * senselDimHeight.value) + '\n'
	print (sMesg)

	# fetch the current calibration range of the sensor (calibrated min/max pressures)
	XSCore90.XS_GetConfigInfo(pressureUnits, ctypes.byref(minPressureRange), ctypes.byref(maxPressureRange))
	sMesg = '\tMin pressure {:0.4f} '.format(float(minPressureRange.value)) + sPressureUnits + ' Max pressure {:0.4f} '.format(float(maxPressureRange.value)) + sPressureUnits
	print (sMesg)
	
	sensorIndex = sensorIndex + 1

# Okay time to retrieve some frames of data	

# before opening the connection, set a frame rate. Its in terms of frames per minute. So a 100 Hz rate means (100 x 60 => 6000 frames per minute)
# Open a connection to the configured sensor(s) - we'll ask for 10 Hz or 600 frames per minute

if XSCore90.XS_OpenConnection(framesPerMinute) != 0:

	# For demo purposes, we're requesting just 2 frames of data
	frameNumber = 0
	maxFrames = 4
	prevsampleMinute = 0
	prevsampleSecond = 0
	prevsampleMillisecond = 0

	while frameNumber < maxFrames:

		# request the sample - this call blocks until the samples are buffered
		if XSCore90.XS_Sample() == 0:
		
			if XSCore90.XS_IsConnectionThreaded() != 0:
				if XSCore90.XS_GetLastErrorCode() == XSCore90.XSErrorCodes.eXS_ERRORCODE_SENSORS_NOSAMPLE.value:
					# this just means the sample is not available
					time.sleep(0.1)
					continue

			# else bad State
			print ("XS_Sample failed.  ERRORCODE= {}".format(XSCore90.XS_GetLastErrorCode()))
			break

		# otherwise we have a sample

		# fetch the sample timestamp
		XSCore90.XS_GetSampleTimestampUTC(ctypes.byref(sampleYear), ctypes.byref(sampleMonth), ctypes.byref(sampleDay), ctypes.byref(sampleHour), ctypes.byref(sampleMinute), ctypes.byref(sampleSecond), ctypes.byref(sampleMillisecond))

		if XSCore90.XS_IsConnectionThreaded() != 0:
			if sampleYear.value == 0:
				# no new sample
				continue

			if ((sampleMinute == prevsampleMinute) and (sampleSecond == prevsampleSecond) and (sampleMillisecond == prevsampleMillisecond)):
				sMesg = 'current= ' + '{:02d}'.format(sampleSecond.value) + ' previous= ' + '{:02d}'.format(prevsampleSecond.value)
				print (sMesg)
				continue # same Timestamp

			prevsampleMinute = sampleMinute
			prevsampleSecond = sampleSecond
			prevsampleMillisecond = sampleMillisecond

		frameNumber = frameNumber + 1

		sMesg = 'Timestamp: ' + str(sampleYear.value) + '-{:02d}'.format(sampleMonth.value) + '-{:02d}'.format(sampleDay.value) + 'T{:02d}'.format(sampleHour.value) + ':{:02d}'.format(sampleMinute.value) + ':{:02d}'.format(sampleSecond.value) + '.{:03d}'.format(sampleMillisecond.value)
		print (sMesg)
			
		# each configured sensor has its own frame buffer
		sensorIndex = 0
		while sensorIndex < nbrSensors:
			
			# fetch the sensor Product ID (PID)
			sensorPID = XSCore90.XS_ConfigSensorPID(sensorIndex)
			sensorIndex = sensorIndex + 1
				
			# need the sensor dimensions to pre-allocate some buffer space
			XSCore90.XS_GetSensorDimensions(sensorPID, ctypes.byref(senselRows), ctypes.byref(senselColumns))
				
			# construct a frame buffer for this sensor
			frameBuffer = (ctypes.c_float*(senselRows.value*senselColumns.value))()

			print ('\nCalling XS_GetPressure')
				
			# retrieve the recorded frame
			if XSCore90.XS_GetPressure(sensorPID, ctypes.byref(frameBuffer)) == 1:

				# now dump the frame to the console window
				for row in range(senselRows.value):
					for column in range(senselColumns.value):
						pressure.value = frameBuffer[row * senselColumns.value + column]

						if pressure.value < 0: # this is a dead cell (outside the scanning range)
							sMesg = '---- '
						else:
							sMesg = '{:0.2f} '.format(pressure.value)
						print (sMesg, end='')
							
					print ('') # line break for end of row
	
	#  finished with the demonstration. Close the connection
	XSCore90.XS_CloseConnection()

# call ExitLibrary to free any resources used by the DLL
XSCore90.XS_ExitLibrary()
