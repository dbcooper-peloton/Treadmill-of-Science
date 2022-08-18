# ===========================================================================
# Demonstration of Python 3.6 wrapper for the XSNReader DLL (32 or 64 bits)
# Implemented as per https://docs.python.org/3/library/ctypes.html
#
# Copyright (C) 2010-2021  XSENSOR Technology Corporation. All rights reserved.
# ===========================================================================
# This file demonstrates use of the XSNReader API
# ===========================================================================

import ctypes
import XSNReader
# C++ programmer note: the import XSNReader imports the wrapper script and runs it.

# ===========================================================================
# Demo Usage
#
# This file demonstrates how to use the Python DLL wrapper to retrieve
# pressure frames from an XSENSOR data file (XSN).
# ===========================================================================

# Initialize the DLL library
result = XSNReader.XSN_InitLibrary()

# pre-define some variables to hold data from the DLL. This is for 
sensorPID = 0
sensorIndex = 0
senselRows = ctypes.c_ushort()
senselColumns = ctypes.c_ushort()
heightCM = ctypes.c_float()
widthCM = ctypes.c_float()
padCount = ctypes.c_ubyte()

pressure = ctypes.c_float() # pressure values only

wMajor = ctypes.c_ushort()
wMinor = ctypes.c_ushort()

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

# query the DLL version (for XSENSOR support reference)
wMajor = XSNReader.XSN_GetLibraryMajorVersion()
wMinor = XSNReader.XSN_GetLibraryMinorVersion()

sVersion = 'DLL Version ' + str(wMajor) + '.' + str(wMinor) + '\n'
print (sVersion)

# load a session file

if XSNReader.XSN_LoadSessionU(r"C:\Users\AndyKind\Documents\GitHub\Project-Orchid\XSensor\ToS\X_log.xsn"):

	# fetch information about the session
	sMesg = 'Session contains ' + str(XSNReader.XSN_FrameCount()) + ' frames'
	print (sMesg)

	sMesg = 'Session contains ' + str(XSNReader.XSN_PadCount()) + ' pads'
	print (sMesg)

	padCount = XSNReader.XSN_PadCount()

	for pad in range(padCount):
		# bool XSN_GetPadInfoEx(uint8_t pad, wchar_t* sModel, uint32_t& nModelLength, wchar_t* sProductID, uint32_t& nProductLength, wchar_t* sSerial, uint32_t& nSerialLength);
		# fetch the sensor name - first get the string buffer size
		XSNReader.XSN_GetPadInfoEx(pad, None, ctypes.byref(nModelLength), None, ctypes.byref(nProductLength), None, ctypes.byref(nSerialLength))
	
		# construct string buffers
		sModel =  (ctypes.c_wchar*(nModelLength.value))()
		sProductID =  (ctypes.c_wchar*(nProductLength.value))()
		sSerial =  (ctypes.c_wchar*(nSerialLength.value))()
		
		# retrieve the strings
		XSNReader.XSN_GetPadInfoEx(pad, ctypes.byref(sModel), ctypes.byref(nModelLength), ctypes.byref(sProductID), ctypes.byref(nProductLength), ctypes.byref(sSerial), ctypes.byref(nSerialLength))

		# determine the measurement dimensions of a single sensor cell (called a Sensel)
		XSNReader.XSN_GetPadSenselDims(pad, ctypes.byref(widthCM), ctypes.byref(heightCM))

		sMesg = 'Pad' + str(pad) + '[' + sModel.value + ' '+ sProductID.value + ' '+ sSerial.value + '] has ' + str(XSNReader.XSN_Rows(pad)) + ' rows; ' + str(XSNReader.XSN_Columns(pad)) + ' columns.'
		print (sMesg)

		padWidth = widthCM.value * float(XSNReader.XSN_Columns(pad))
		padHeight = heightCM.value * float(XSNReader.XSN_Rows(pad))

		sMesg = 'Pad dims: {:0.3f}'.format(padWidth) + 'cm width x {:0.3f}'.format(padHeight) + 'cm length\n'
		print (sMesg)


	sMesg = 'Session base pressure units is ' + str(XSNReader.XSN_GetPressureUnits())
	print (sMesg)

	XSNReader.XSN_SetPressureUnits(XSNReader.EXSNPressureUnit.eXSNPRESUNIT_KGCM2.value);

	frameCount = XSNReader.XSN_FrameCount()

	# limit our output to 3 frames
	if frameCount > 3:
		frameCount = 3

	frame = 1

	while frame <= frameCount:
		sMesg = '\nStep to Frame ' + str(frame)
		print (sMesg)

		# Step to the frame
		if XSNReader.XSN_StepToFrame(frame) == 0:
			sMesg = 'Step to Frame failed'
			print (sMesg)
	
		frameID = XSNReader.XSN_GetFrameID()

		sMesg = 'Processing Frame ID ' + str(frameID)
		print (sMesg)

		XSNReader.XSN_GetTimeStampUTC(ctypes.byref(nYear), ctypes.byref(nMonth), ctypes.byref(nDay), ctypes.byref(nHour), ctypes.byref(nMinute), ctypes.byref(nSecond), ctypes.byref(nMilliseconds))

		sMesg = 'Frame Timestamp: ' + str(nYear.value) + '-{:02d}'.format(nMonth.value) + '-{:02d}'.format(nDay.value) + 'T{:02d}'.format(nHour.value) + ':{:02d}'.format(nMinute.value) + ':{:02d}'.format(nSecond.value) + '.{:03d}'.format(nMilliseconds.value)			
		print (sMesg)

		for pad in range(padCount):
			senselColumns = XSNReader.XSN_Columns(pad);
			senselRows = XSNReader.XSN_Rows(pad);

			# retrieve the recorded frame

			# construct a frame buffer for this sensor .. should probably cache this?
			frameBuffer = (ctypes.c_float*(XSNReader.XSN_Columns(pad) * XSNReader.XSN_Rows(pad)))()

			if XSNReader.XSN_GetPressureMapEx(pad, ctypes.byref(frameBuffer), ctypes.byref(frameBufferSize)) == 1:
				print ('Got pressure frame')

				# now dump the frame to the console window
				for row in range(senselRows):
					for column in range(senselColumns):
						pressure.value = frameBuffer[row * senselColumns + column]
						sMesg = '{:0.2f}, '.format(pressure.value)
						print (sMesg, end='')
							
					print ('') # line break for end of row

		frame += 1


	XSNReader.XSN_CloseSession()

# call ExitLibrary to free any resources used by the DLL
XSNReader.XSN_ExitLibrary()
