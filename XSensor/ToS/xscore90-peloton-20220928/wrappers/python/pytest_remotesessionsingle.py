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
# Usage
#
# This file demonstrates starting and stopping of a remote X4 session.
# ===========================================================================

# Initialize the DLL library
# - pass in 1 for threaded mode, and 0 otherwise
result = XSCore90.XS_InitLibrary(1)

# pre-define some variables to hold data from the DLL.
sensorPID = ctypes.c_ulonglong()
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

print ("Running remote session single insole test")
print ("Setting calibration cache...")

sCalCacheFolder = "e:\CalCache"
XSCore90.XS_SetCalibrationFolderUTF8(sCalCacheFolder.encode('utf-8'))

framesPerMinute = 10 * 60	# 10 Hz or 600 frames per minute

enableIMU = False
wirelessX4 = False

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

# if you're testing X4 insole sensor, you can use this
if enableIMU:
	XSCore90.XS_SetEnableIMU(1) # if we want IMU data with each frame

# we'll work in PSI for this demo
sPressureUnits = str(XSCore90.EPressureUnit.ePRESUNIT_PSI)
pressureUnits = ctypes.c_ubyte(XSCore90.EPressureUnit.ePRESUNIT_PSI.value)
XSCore90.XS_SetPressureUnit(ctypes.c_ubyte(XSCore90.EPressureUnit.ePRESUNIT_PSI.value))

# lets not interrupt any X4's that are presently remote recording
XSCore90.XS_SetAllowEnumInterruptX4Remote(0)

# scan for available sensors - can take a while as it tries all known connections
sensorCount = XSCore90.XS_EnumSensors()
if sensorCount == 0:
	print ("No available sensors found for remote test.")
	print ("\nEND OF LINE")
	exit()


bFound = False
bFootSensor = ctypes.c_ubyte()
bLeftFoot = ctypes.c_ubyte()

# we'll connect to the first X4 we find
for sensor in range(0, sensorCount):
	sensorPID = XSCore90.XS_EnumSensorPID(sensor)

	if XSCore90.XS_IsX4FootSensor(sensorPID, ctypes.byref(bFootSensor), ctypes.byref(bLeftFoot)) != 0:
		if bFootSensor.value == 1:
			bFound = True

			# fetch the buffer size for the sensor name buffer
			XSCore90.XS_GetSensorNameUTF8(sensorPID, ctypes.byref(nameBufferSize), None)
	
			# construct a buffer for the name
			nameBuff =  (ctypes.c_char*(nameBufferSize.value))()

			# retrieve the name as a UTF8 string
			XSCore90.XS_GetSensorNameUTF8(sensorPID, ctypes.byref(nameBufferSize), ctypes.byref(nameBuff))
			sensorName = str(nameBuff.value.decode('utf-8'))

			print ("Found X4 foot sensor " + sensorName)
			break # just need one for this demo

if bFound == False:
	print ("No X4 foot sensors found with active SD cards")
	print ("\nEND OF LINE")
	exit()

# Open a connection to the X4
if XSCore90.X4_OpenRemote(sensorPID) == 0:
	print ("X4 remote command failed. ERRORCODE= {}".format(XSCore90.XS_GetLastErrorCode()))
	print ("\nEND OF LINE")
	exit()

# check if a recording is in progress
remoteRecording = ctypes.c_ubyte() # XBOOL

if XSCore90.X4_IsRemoteRecording(sensorPID, ctypes.byref(remoteRecording)) != 0:

	sMesg = "X4 remote recording session is "

	if remoteRecording.value != 0:
		sMesg += "active"
	else:
		sMesg += "not active"
	
	print (sMesg)

	if remoteRecording.value != 0:
		print ("Stopping X4 remote recording")
		XSCore90.X4_StopRemoteRecording(sensorPID)

		# now close the connection
		XSCore90.X4_CloseRemote(sensorPID)

		print ("\nEND OF LINE")
		exit()
else:
	print ("X4 remote command failed. ERRORCODE= {}".format(XSCore90.XS_GetLastErrorCode()))
	print ("\nEND OF LINE")
	exit()

print ("Prepping for X4 remote recording")

frameRateHz = 40.0

if XSCore90.X4_StartRemoteRecording(sensorPID, frameRateHz) != 0:

	print ("X4 remote recording started")

	# give it some time to generate some frames
	time.sleep(0.1)

	print ("Fetching preview frame")

	if XSCore90.X4_SampleRemote(sensorPID) != 0:

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

else:
	print ("X4 remote command failed. ERRORCODE= {}".format(XSCore90.XS_GetLastErrorCode()))

# close the connection
XSCore90.X4_CloseRemote(sensorPID)

# call ExitLibrary to free any resources used by the DLL
XSCore90.XS_ExitLibrary()

print ("script completed")

print ("\nEND OF LINE")
exit()
