# ===========================================================================
# Python 3.6 wrapper for the XSNReader DLL
# Implemented as per https:#docs.python.org/3/library/ctypes.html
#
#  This software is provided 'as-is', without any express or implied
#  warranty.  In no event will XSENSOR Technology Corporation be held liable
#  for any damages arising from the use of this software.
#
#  Permission is granted to any Licensee of the XSENSOR PRO 8 software
#  to use this software (XSNReader.dll and XSNReader64.dll) for any
#  non-commercial purpose, subject to the following terms and restrictions:
#
#  1. The Licensee agrees that this software is covered by the terms and
#     restrictions of the Software License Agreement covering the XSENSOR PRO 8 Software.
#
# Copyright (C) 2010-2022  XSENSOR Technology Corporation. All rights reserved.
# ===========================================================================

import ctypes
from enum import Enum

# path for importing 64 bit DLL

# Path for Daniel's PC
path = r"C:\Users\DanielCooper\PycharmProjects\pythonProject2\XSNReader64.dll"

# Path for Andy's PC
# path = r"C:\Users\AndyKind\Documents\GitHub\Project-Orchid\XSensor\ToS\XSNReader64.dll"

# Path for TOS PC
# path = r"C:\Users\preco\OneDrive\Desktop\Project-Orchid\XSensor\ToS\XSNReader64.dll"


class EXSNPressureUnit(Enum):
	eXSNPRESUNIT_MMHG	= 0	# millimeters of mercury
	eXSNPRESUNIT_INH2O = 1	# inches of water
	eXSNPRESUNIT_PSI	= 2	# pounds/sq.inch
	eXSNPRESUNIT_KPA	= 3	# kilopascals
	eXSNPRESUNIT_KGCM2	= 4	# kgf/cm^2
	eXSNPRESUNIT_ATM	= 5	# atmospheres
	eXSNPRESUNIT_NCM2	= 6	# newtons/cm^2
	eXSNPRESUNIT_MBAR	= 7	# millibars
	eXSNPRESUNIT_NM2	= 8	# Newton/meter^2
	eXSNPRESUNIT_GCM2	= 9	# grams/cm^2
	eXSNPRESUNIT_BAR	= 10 # bar
	eXSNPRESUNIT_RAW 	= 255 # non-calibrated readings from the sensors - 16 bit integers

# force/load units
class EXSNForceUnit(Enum):
	eXSNFORCEUNIT_UNKNOWN = 0	#  raw pressure values?
	eXSNFORCEUNIT_NEWTONS = 1	# newtons
	eXSNFORCEUNIT_KGF     = 2  # kilograms of force
	eXSNFORCEUNIT_LBF     = 10	# pound-force

class EXSNReaderErrorCodes(Enum):
	eXSN_ERRORCODE_OK = 0						# Function ran normally
	eXSN_ERRORCODE_LIBRARY_NOT_INITIALIZED = 1	# The DLL library has not been initialized
	eXSN_ERRORCODE_INVALID_XSN = 2				# LoadSession failed because the session is not a valid xsensor file
	eXSN_ERRORCODE_INVALID_VERSION = 3			# LoadSession failed because the session is a valid xsensor file, but the version is not supported.
	eXSN_ERRORCODE_UNSUPPORTED_SENSOR = 4		# The reader DLL does not support the sensor model found in the XSN.
	eXSN_ERRORCODE_NOSESSION = 5				# The operation failed because no session has been loaded.
	eXSN_ERRORCODE_EMPTYSESSION = 6				# The operation failed because there are no frames in this session
	eXSN_ERRORCODE_BADPARAMETER_OUTOFRANGE = 7	# a parameter is out of range
	eXSN_ERRORCODE_BADPARAMETER_NULL  = 8		# null parameter - pass in a variable/buffers address
	eXSN_ERRORCODE_MEMORYALLOCATION_FAILED = 9	# the system seems to be running low on memory, or the DLL could not allocate some memory


# ===========================================================================
# load the library. Change the path if you want to put it in another folder.
# ===========================================================================

# import the 64 bit dll
libXSN = ctypes.cdll.LoadLibrary(path)


# ===========================================================================
#	Library initialization/deinitialization
# ===========================================================================

# Retrieves the last error code.  Check this value when a function reports a failure.  (see enum EXSNReaderErrorCodes).
XSN_GetLastErrorCode = libXSN.XSN_GetLastErrorCode
XSN_GetLastErrorCode.restype = ctypes.c_uint


# XSN_InitLibrary
# Initialize the library.  This must be the first call to the Library
# bool XSN_InitLibrary();
XSN_InitLibrary = libXSN.XSN_InitLibrary
XSN_InitLibrary.restype = ctypes.c_ubyte


# XSN_ExitLibrary
# Uninitializes the library, freeing all allocated resources.  This should be the last call to the Library
# bool XSN_ExitLibrary();
XSN_ExitLibrary = libXSN.XSN_ExitLibrary
XSN_ExitLibrary.restype = ctypes.c_ubyte


# XSN_GetLibraryMajorVersion
# returns the library's major version number
# uint16_t XSN_GetLibraryMajorVersion();
XSN_GetLibraryMajorVersion = libXSN.XSN_GetLibraryMajorVersion
XSN_GetLibraryMajorVersion.restype = ctypes.c_ushort

# XSN_GetLibraryMinorVersion
# returns the library's minor version number
# uint16_t XSN_GetLibraryMinorVersion();
XSN_GetLibraryMinorVersion = libXSN.XSN_GetLibraryMinorVersion
XSN_GetLibraryMinorVersion.restype = ctypes.c_ushort


# ===========================================================================
# Session Initialization
# ===========================================================================

# XSN_LoadSessionU
# loads an xsensor data file
# Resets the pressure units to the base ones used in the session file
# Returns true (non-zero) if the load is successful
# bool XSN_LoadSessionU(const wchar_t* szSession);
XSN_LoadSessionU = libXSN.XSN_LoadSessionU
XSN_LoadSessionU.argtypes = [ctypes.c_wchar_p]
XSN_LoadSessionU.restype = ctypes.c_ubyte

# XSN_CloseSession
# unloads the current session file. Frees the file handle so the file can be accessed elsewhere.
# bool XSN_CloseSession();
XSN_CloseSession = libXSN.XSN_CloseSession
XSN_CloseSession.restype = ctypes.c_ubyte


# ===========================================================================
#	Session Configuration
# ===========================================================================

# XSN_FrameCount
# Returns the number of frames in the session file.
# uint32_t XSN_FrameCount();
XSN_FrameCount = libXSN.XSN_FrameCount
XSN_FrameCount.restype = ctypes.c_uint

# XSN_PadCount
# Returns the number of pads in the session file
# uint8_t XSN_PadCount();
XSN_PadCount = libXSN.XSN_PadCount
XSN_PadCount.restype = ctypes.c_ubyte

# XSN_GetPadInfoEx
# fetch info about the sensors
# bool XSN_GetPadInfoEx(uint8_t pad, wchar_t* sModel, uint32_t& nModelLength, wchar_t* sProductID, uint32_t& nProductLength, wchar_t* sSerial, uint32_t& nSerialLength);
# If the buffers are set to None, the length of the require buffer (in unicode16 char counts + 1) is returned.
XSN_GetPadInfoEx = libXSN.XSN_GetPadInfoEx
XSN_GetPadInfoEx.argtypes = [ctypes.c_ubyte, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
XSN_GetPadInfoEx.restype = ctypes.c_ubyte
# USAGE: 
#
#   # retrieve the buffer sizes
#   nModelLength = ctypes.c_uint()
#   nProductLength = ctypes.c_uint()
#   nSerialLength = ctypes.c_uint()
#
# 	XSN_GetPadInfoEx(padIndex, None, ctypes.byref(nModelLength), None, ctypes.byref(nProductLength), None, ctypes.byref(nSerialLength))
#
#   # retrieve the strings
#	sModel =  (ctypes.c_wchar*(nModelLength.value))()
#	sProductID =  (ctypes.c_wchar*(nProductLength.value))()
#	sSerial =  (ctypes.c_wchar*(nSerialLength.value))()
#
# 	XSN_GetPadInfoEx(padIndex, ctypes.byref(sModel), ctypes.byref(nModelLength), ctypes.byref(sProductID), ctypes.byref(nProductLength), ctypes.byref(sSerial), ctypes.byref(nSerialLength))


# XSN_GetPadSenselDims
# width and height of a single cell (a sensel) in centimetres
# bool XSN_GetPadSenselDims(uint8_t pad, float& widthCM, float& heightCM);
XSN_GetPadSenselDims = libXSN.XSN_GetPadSenselDims
XSN_GetPadSenselDims.argtypes = [ctypes.c_ubyte, ctypes.c_void_p, ctypes.c_void_p]
XSN_GetPadSenselDims.restype = ctypes.c_ubyte


# XSN_IsFootSensor
# Returns true if the pad is a foot sensor.  bLeftSensor = false when its a right foot sensor.
# bool XSN_IsFootSensor(uint8_t pad, bool& bLeftSensor);
XSN_IsFootSensor = libXSN.XSN_IsFootSensor
XSN_IsFootSensor.argtypes = [ctypes.c_ubyte, ctypes.c_void_p]
XSN_IsFootSensor.restype = ctypes.c_ubyte

# XSN_Rows
# Returns the number of rows associated with the pad index (0 based index)
# uint16_t XSN_Rows(uint8_t pad);
XSN_Rows = libXSN.XSN_Rows
XSN_Rows.argtypes = [ctypes.c_ubyte]
XSN_Rows.restype = ctypes.c_ushort

# XSN_Columns
# Returns the number of columns associated with the pad index (0 based index)
# uint16_t XSN_Columns(uint8_t pad);
XSN_Columns = libXSN.XSN_Columns
XSN_Columns.argtypes = [ctypes.c_ubyte]
XSN_Columns.restype = ctypes.c_ushort


# XSN_GetPressureUnits
# Returns the current pressure units (see EXSNPressureUnit).
# EXSNPressureUnit XSN_GetPressureUnits();
XSN_GetPressureUnits = libXSN.XSN_GetPressureUnits
XSN_GetPressureUnits.restype = ctypes.c_ubyte

# XSN_SetPressureUnits
# Sets the pressure unit format of the pressure values
# Pass in a value of type EXSNPressureUnit
# bool XSN_SetPressureUnits(uint8_t PressureUnit);
XSN_SetPressureUnits = libXSN.XSN_SetPressureUnits
XSN_SetPressureUnits.argtypes = [ctypes.c_ubyte]

# XSN_GetForceUnits
# Returns the load or force units (EXSNForceUnit) that correspond to the current pressure units
# EXSNPressureUnit XSN_GetForceUnits();
XSN_GetForceUnits = libXSN.XSN_GetForceUnits
XSN_GetForceUnits.restype = ctypes.c_ubyte

# XSN_GetMaxPressure
# Returns the maximum pressure the file was calibrated for. (If raw, then 65534.0f)
# float XSN_GetMaxPressure();
XSN_GetMaxPressure = libXSN.XSN_GetMaxPressure
XSN_GetMaxPressure.restype = ctypes.c_float

# XSN_GetMinPressure
# Returns the minimum pressure the file was calibrated for. (If raw, then 0.0f)
# Values below this pressure are considered uncalibrated.
# float XSN_GetMinPressure();
XSN_GetMinPressure = libXSN.XSN_GetMinPressure
XSN_GetMinPressure.restype = ctypes.c_float

# XSN_GetZeroThreshold
# Returns the file's zero threshold pressure. Values below this threshold are considered to be zero.
# float XSN_GetZeroThreshold();
XSN_GetZeroThreshold = libXSN.XSN_GetZeroThreshold
XSN_GetZeroThreshold.restype = ctypes.c_float


# XSN_GetGeneralNotesEx
# Retrieves any general notes set in the session (if any)
# See XSN_GetPadInfoEx on parameter usage
# bool XSN_GetGeneralNotesEx(wchar_t* sNotes, uint32_t& nNotesLength);
XSN_GetGeneralNotesEx = libXSN.XSN_GetGeneralNotesEx
XSN_GetGeneralNotesEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
XSN_GetGeneralNotesEx.restype = ctypes.c_ubyte


# XSN_GetFrameNotesEx
# Retrieves any notes specific to the current frame
# See XSN_GetPadInfoEx on parameter usage
# bool XSN_GetFrameNotesEx(wchar_t* sNotes, uint32_t& nNotesLength);
XSN_GetFrameNotesEx = libXSN.XSN_GetFrameNotesEx
XSN_GetFrameNotesEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
XSN_GetFrameNotesEx.restype = ctypes.c_ubyte


# ===========================================================================
#	Frame navigation
# ===========================================================================

# XSN_StepToFrame
# Steps to the frame (1 based index)
# bool XSN_StepToFrame(uint32_t nFrame);
XSN_StepToFrame = libXSN.XSN_StepToFrame
XSN_StepToFrame.argtypes = [ctypes.c_uint]
XSN_StepToFrame.restype = ctypes.c_ubyte

# XSN_GetFrameID
# Retrieves the current frame ID (or zero if no frame)
# uint32_t XSN_GetFrameID();
XSN_GetFrameID = libXSN.XSN_GetFrameID
XSN_GetFrameID.restype = ctypes.c_uint

# XSN_GetSessionID
# The start-stop session to which the current frame belongs (zero if no frame)
# Use this to detect recording gaps due to recording stoppage and restart
# uint16_t XSN_GetSessionID();
XSN_GetSessionID = libXSN.XSN_GetSessionID
XSN_GetSessionID.restype = ctypes.c_ushort

# XSN_GetTimeStampUTC
# Retrieves the timestamp associated with the current frame - in UTC format
# bool XSN_GetTimeStampUTC(uint16_t& nYear, uint16_t& nMonth, uint16_t& nDay, uint16_t& nHour, uint16_t& nMinute, uint16_t& nSecond, uint16_t& nMilliseconds);
XSN_GetTimeStampUTC = libXSN.XSN_GetTimeStampUTC
XSN_GetTimeStampUTC.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
XSN_GetTimeStampUTC.restype = ctypes.c_ubyte

# XSN_GetTimeStampUTCuS
# Retrieves the timestamp associated with the current frame - in UTC format
# bool XSN_GetTimeStampUTCuS(uint16_t& nYear, uint16_t& nMonth, uint16_t& nDay, uint16_t& nHour, uint16_t& nMinute, uint16_t& nSecond, uint16_t& nMilliseconds, uint16_t& wMicrosecs);
XSN_GetTimeStampUTCuS = libXSN.XSN_GetTimeStampUTCuS
XSN_GetTimeStampUTCuS.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
XSN_GetTimeStampUTCuS.restype = ctypes.c_ubyte

# ===========================================================================
#	Pressure Map Access
# ===========================================================================

# XSN_GetPressureMapEx
# Retrieves the pressure map. nMapElementCount is the number of element required for the pressure map.
# Set pPressureMap to None to just retrieve the nMapElementCount.
# nMapElementCount = XSN_Rows(pad) * XSN_Columns(pad);
# bool XSN_GetPressureMapEx(uint8_t pad, float* pPressureMap, uint32_t& nMapElementCount);
XSN_GetPressureMapEx = libXSN.XSN_GetPressureMapEx
XSN_GetPressureMapEx.argtypes = [ctypes.c_ubyte, ctypes.c_void_p, ctypes.c_void_p]
XSN_GetPressureMapEx.restype = ctypes.c_ubyte

# ===========================================================================
#	Pressure Map Statistics
# ===========================================================================

# These functions return the statistics for the current pressure map.
# If there is an error, -1.0f is returned for all stats functions. Call XSN_GetLastErrorCode() if that occurs.
# The pressure readings below the zero threshold are treated as zero.
# The zero threshold should be in the same units as XSN_GetPressureUnits().

# XSN_GetStatAvgPressure
# Return the average pressure of the pressure map. Zero pressure cells are not included in the statistic.
# float XSN_GetStatAvgPressure(uint8_t pad, float nZeroThreshold);
XSN_GetStatAvgPressure = libXSN.XSN_GetStatAvgPressure
XSN_GetStatAvgPressure.argtypes = [ctypes.c_ubyte, ctypes.c_float]
XSN_GetStatAvgPressure.restype = ctypes.c_float

# XSN_GetStatPeakPressure
# Return the peak/maximum pressure on the pressure map.
# float XSN_GetStatPeakPressure(uint8_t pad, float nZeroThreshold);
XSN_GetStatPeakPressure = libXSN.XSN_GetStatPeakPressure
XSN_GetStatPeakPressure.argtypes = [ctypes.c_ubyte, ctypes.c_float]
XSN_GetStatPeakPressure.restype = ctypes.c_float

# XSN_GetStatMinPressure
# Return the minimum pressure on the pressure map. Zero pressure cells are not included in the statistic.
# float XSN_GetStatMinPressure(uint8_t pad, float nZeroThreshold);
XSN_GetStatMinPressure = libXSN.XSN_GetStatMinPressure
XSN_GetStatMinPressure.argtypes = [ctypes.c_ubyte, ctypes.c_float]
XSN_GetStatMinPressure.restype = ctypes.c_float


# XSN_GetStatContactAreaCM
# Return the area (centimeters) of the pressure map with pressure at or above the zero threshold.
# Zero pressure cells are not included in the statistic.
# float XSN_GetStatContactAreaCM(uint8_t pad, float nZeroThreshold);
XSN_GetStatContactAreaCM = libXSN.XSN_GetStatContactAreaCM
XSN_GetStatContactAreaCM.argtypes = [ctypes.c_ubyte, ctypes.c_float]
XSN_GetStatContactAreaCM.restype = ctypes.c_float


# XSN_GetStatEstimatedLoad
# Return the estimated load (force) applied to the sensor.
# Zero pressure cells are not included in the statistic.
# Call XSN_GetForceUnits() to determine the units of the load statistic.
# float XSN_GetStatEstimatedLoad(uint8_t pad, float nZeroThreshold);
XSN_GetStatEstimatedLoad = libXSN.XSN_GetStatEstimatedLoad
XSN_GetStatEstimatedLoad.argtypes = [ctypes.c_ubyte, ctypes.c_float]
XSN_GetStatEstimatedLoad.restype = ctypes.c_float


# XSN_GetCOP
# Computes the center of pressure (COP) and returns its column and row coordinates.
# Returns negative coordinates if there is a problem. Call XSN_GetLastErrorCode() if that occurs.
# bool XSN_GetCOP(uint8_t pad, float nZeroThreshold, float& column, float& row);
XSN_GetCOP = libXSN.XSN_GetCOP
XSN_GetCOP.argtypes = [ctypes.c_ubyte, ctypes.c_float, ctypes.c_void_p, ctypes.c_void_p]
XSN_GetCOP.restype = ctypes.c_ubyte


# Computes the center of pressure (COP) and returns its column and row coordinates.
# Returns negative coordinates if there is a problem. Call XSN_GetLastErrorCode() if that occurs.
#
# The center of pressure calculation ignores pressure which is below the zero threshold.
# Row coordinates are from 1 to XSN_Rows()
# Column coordinates are from 1 to XSN_Columns()
#
# Whole numbers (no fractions) indicate the COP is over the center of the sensel.
#
# The fractional part of the coordinate indicates a normalized distance between
# the centers of two sensels.
#
# Example
# Suppose the function returns these values: column = 1.53f; row = 2.25f.
# This means the COP is 53% of the distance between the center of column 1 and
# the center of column 2. The COP is 25% of the distance between the center
# of row 2 and the center of row 3. (It is closer to row 2).

# ===========================================================================
# END OF FILE
# ===========================================================================
