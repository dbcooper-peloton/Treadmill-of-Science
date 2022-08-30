# ===========================================================================
# Python 3.6 wrapper for the XSCore90 DLL
# Implemented as per https:#docs.python.org/3/library/ctypes.html
#
# Copyright (C) 2010-2022  XSENSOR Technology Corporation. All rights reserved.
# ===========================================================================

import ctypes
from enum import Enum

class EXSErrorCodes(Enum):
	eXS_ERRORCODE_OK							= 0	# Function ran normally
	eXS_ERRORCODE_BADPARAMETER_OUTOFRANGE		= 1 # a parameter is out of range
	eXS_ERRORCODE_BADPARAMETER_NULL				= 2 # null parameter - pass in a variable/buffers address
	eXS_ERRORCODE_BADPARAMETER_INVALID_SENSOR_PID = 3 # either the PID is bad or the sensor was not configured
	eXS_ERRORCODE_CALFILE_LOADFAILED			= 4 # calibration file failed to load - likely the file wasn't found
	eXS_ERRORCODE_CALFILE_DOESNOTMATCHSENSOR	= 5 # the calibration file does not match the sensor
	eXS_ERRORCODE_CONFIGURATION_NOTCOMPLETE		= 6 # Call XS_ConfigComplete() to complete the sensor configuration.
	eXS_ERRORCODE_CONFIGURATION_NOSENSORS		= 7 # no sensors have been added to the sample config via XS_AddSensorToConfig() or could not be added
	eXS_ERRORCODE_CONFIGURATION_FAILCREATEXSN   = 8 # Could not create the XSN file. Check that the path is valid and the location can be written too.
	eXS_ERRORCODE_SENSORS_SENSORNOTFOUND		= 9 # either the sensor isn't enumerated or the PID is invalid
	eXS_ERRORCODE_SENSORS_RAWONLY				= 10 # XS_GetPressure() called but no calibration files have been loaded.  Only raw data is available.
	eXS_ERRORCODE_SENSORS_NOSAMPLE				= 11 # XS_Sample() has not been called yet or it has not succeeded in retrieving a sample
	eXS_ERRORCODE_SENSORS_CONNECTIONLOST		= 12 # XS_Sample failed because a sensor was disconnected or USB power reset
	eXS_ERRORCODE_SENSORS_SAMPLETIMEOUT			= 13 # XS_Sample failed because the sensor timed out while reading
	eXS_ERRORCODE_SENSORS_SAMPLEFAILED			= 14 # XS_Sample failed for reasons unknown
	eXS_ERRORCODE_SENSORS_NOCONNECTION			= 15 # Calling XS_Sample() without first calling to XS_OpenConnection()?
	eXS_ERRORCODE_SENSORS_CONNECTFAILED			= 16 # It's possible that one of the sensors has become disconnected.  Check connections.
	eXS_ERRORCODE_MEMORYALLOCATION_FAILED		= 17 # the system seems to be running low on memory or the DLL could not allocate some memory
	eXS_ERRORCODE_LIBRARY_NOT_INITIALIZED		= 18 # The DLL library has not been initialized
	eXS_ERRORCODE_AUTOCONFIG_SENSORNOTFOUND		= 19 # no sensors found during enumeration - please check XS_GetLastEnumState()
	eXS_ERRORCODE_COULDNOTCREATECAPTUREFILE		= 20 # Could not create the target capture file
	eXS_ERRORCODE_SIMFILE_LOADFAIL				= 21 # A problem occured while loading the simulation file.  The path might be incorrect or the file cannot be opened.  (Try loading it in the XSENSOR desktop software.)
	eXS_ERRORCODE_SIM_FUNCTION_NA				= 22 # The DLL function is not available or does nothing while in simulation mode.
	eXS_ERRORCODE_SIM_CALIBRATED_ONLY			= 23 # The simulation only supports calibrated (pressure) data
	eXS_ERRORCODE_SIM_RAW_ONLY					= 24 # The simulation only supports raw (non-pressure) data
	eXS_ERRORCODE_MANCAL_FUNCTION_NOTSET		= 25 # The manaul calibration state is not set which this function requires.
	eXS_ERRORCODE_MANCAL_FUNCTION_NA			= 26 # The DLL function is not available or does nothing while in manual calibration mode.
	eXS_ERRORCODE_CALIBRATION_AUTOCACHE			= 27 # This calibration function is disabled while the calibration auto-cache is enabled via XS_SetCalibrationFolder.
	eXS_ERRORCODE_X4CONFIGSCRIPT_COULDNOTOPEN	= 28 # The X4 config script could not be opened. Perhaps a bad file path? Or the sensor is not an X4!
	eXS_ERRORCODE_X4CONFIGSCRIPT_BADRESPONSE	= 29 # A command in the X4 config script returned a bad response


# this is a bit mask - any number of these bits might be set
class EEnumerationState(Enum):
	eENUMSTATE_OK						= 0x00000000	# no errors detected
	eENUMSTATE_NOSPKSDETECTED			= 0x00000001	# no SPKS appear in the computer
	eENUMSTATE_OPENDEVICEFAIL			= 0x00000002	# The SPK could not be opened with CreateFile
	eENUMSTATE_OPENDEVICEFAIL_PROCESSLOCK = 0x00000004	# The SPK could not be opened because some other process has it opened
	eENUMSTATE_HIDDEVICEENUMFAIL		= 0x00000008	# The HID device enumerate failed - very low level
	eENUMSTATE_MISSINGCON				= 0x00000010	# The SPK is not connected to a sensor pad
	eENUMSTATE_MISSINGDLLCODE			= 0x00000020	# The sensor does not have a DLL code
	eENUMSTATE_MISMATCHEDDLLCODE		= 0x00000040	# The sensor's DLL code does not match this DLL
	eENUMSTATE_MISSINGPROFILE			= 0x00000080	# The sensors profile is not supported by this DLL
	eENUMSTATE_MISSINGCHILDSPKS			= 0x00000100	# This multi-SPK sensor is missing SPKS ports 2 to N
	eENUMSTATE_MISSINGPARENTSPK			= 0x00000200	# This multi-SPK sensor is missing SPK on port 1
	eENUMSTATE_MISMATCHEEDFIRMWARE		= 0x00000400	# This multi-SPK sensor must the same firmware on each SPK
	eENUMSTATE_MISMATCHEDSPKTYPES		= 0x00000800	# This multi-SPK sensor must the same SPK types on each port (either XS PRO or just XS)
	eENUMSTATE_CONNECTIONSENSE			= 0x00001000	# This sensor pad is not properly plugged into the SPK - or there is a hardware problem with the sensor
	eENUMSTATE_CONREQUIRESNEWERFIRMWARE	= 0x00002000	# The sensor pad requires SPK(s) with firmware 1.3 or better
	eENUMSTATE_MIXEDHSSX3				= 0x00004000,	# Mixed X3 and HSS components (either HSS sensor on X3, or X3 sensor on HSS)
	eENUMSTATE_SENSORLOCK				= 0x00008000,	# The sensor is locked (likely due to time trial expiry)

class EPressureUnit(Enum):
	ePRESUNIT_MMHG	= 0	# millimeters of mercury
	ePRESUNIT_INH2O = 1	# inches of water
	ePRESUNIT_PSI	= 2	# pounds/sq.inch
	ePRESUNIT_KPA	= 3	# kilopascals
	ePRESUNIT_KGCM2	= 4	# kgf/cm^2
	ePRESUNIT_ATM	= 5	# atmospheres
	ePRESUNIT_NCM2	= 6	# newtons/cm^2
	ePRESUNIT_MBAR	= 7	# millibars
	ePRESUNIT_NM2	= 8	# Newton/meter^2
	ePRESUNIT_GCM2	= 9	# grams/cm^2
	ePRESUNIT_RAW 	= 255 # non-calibrated readings from the sensors - 16 bit integers

# ===========================================================================
# load the library. Change the path if you want to put it in another folder.
#
# programmer note: You will probably have to supply the full path to the DLL.
# ===========================================================================

# import the 64 bit dll
# libXSC = ctypes.cdll.LoadLibrary("XSCore90x64.dll")

# import the 32 bit dll
# usage example: libXSC = ctypes.cdll.LoadLibrary("E:\\xsource\\xsensor.libs\\Xsensor.Libraries.X3\\XSCore90\\bin\\Win32\\Debug\\XSCore90.dll")
libXSC = ctypes.cdll.LoadLibrary(r"C:\Users\preco\OneDrive\Desktop\Project-Orchid\XSensor\ToS\XSCore90x64.dll")

# ===========================================================================
#	Library initialization/deinitialization
# ===========================================================================

# Retrieves the last error code.  Check this value when a function reports a failure.  (see enum EXSErrorCodes below).
XS_GetLastErrorCode = libXSC.XS_GetLastErrorCode
XS_GetLastErrorCode.restype = ctypes.c_uint


# XS_InitLibrary
# Initialize the XS software engine.  This must be the first call to the XS Library
# Use bThreadMode set to TRUE(1) if you want the DLL to sample independently of the call to XS_Sample.
# Otherwise set to FALSE(0) to have finer control over the sample rate.
# XBOOL XS_InitLibrary(XBOOL bThreadMode);
XS_InitLibrary = libXSC.XS_InitLibrary
XS_InitLibrary.argtypes = [ctypes.c_ubyte]
XS_InitLibrary.restype = ctypes.c_ubyte


# XS_ExitLibrary
# Uninitializes the XS software engine, freeing all allocated resources.  This should be the last call to the XS Library
# XBOOL XS_ExitLibrary();
XS_ExitLibrary = libXSC.XS_ExitLibrary
XS_ExitLibrary.restype = ctypes.c_ubyte


# XS_GetVersion
# fetches the DLL version - major.minor.build.revision
# XBOOL XS_GetVersion(uint16_t& major, uint16_t& minor, uint16_t& build, uint16_t& revision);
XS_GetVersion = libXSC.XS_GetVersion
XS_GetVersion.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
XS_GetVersion.restype = ctypes.c_ubyte


# ===========================================================================
#	Sensor Enumeration and Information
# ===========================================================================

# XS_EnumSensors
# Enumerates the internal sensor lists.  Scans the USB bus for available sensors.  Returns the number found.
# This function can be called multiple times to refresh the sensor list.
# FYI, this list depends on how fast the computer enumerates devices on the USB bus.
# When you first plug in a sensor, it might take 5 to 10 seconds for it to appear.
# uint32_t XS_EnumSensors();
XS_EnumSensors = libXSC.XS_EnumSensors
XS_EnumSensors.restype = ctypes.c_uint


# When enabled, the DLL skips looking for new sensors and only attempts to talk to sensors it already knows about.
# Use this when you've found a sensor, but lost its connection and want to rescan for it without the delay of looking
# for new sensors.
# void XS_SetAllowFastEnum(XBOOL bAllow);
XS_SetAllowFastEnum = libXSC.XS_SetAllowFastEnum
XS_SetAllowFastEnum.argtypes = [ctypes.c_ubyte]

# XBOOL XS_GetAllowFastEnum();
XS_GetAllowFastEnum = libXSC.XS_GetAllowFastEnum
XS_GetAllowFastEnum.restype = ctypes.c_uint

# XS_GetLastEnumState
# Retrieves the enumeration error state.  This value is only valid after a call to XS_EnumSensors
# uint32_t XS_GetLastEnumState();
XS_GetLastEnumState = libXSC.XS_GetLastEnumState
XS_GetLastEnumState.restype = ctypes.c_uint


# XS_EnumSensorCount
# Returns a count of the number of sensors found during the EnumSensors() call.
# uint32_t XS_EnumSensorCount();
XS_EnumSensorCount = libXSC.XS_EnumSensorCount
XS_EnumSensorCount.restype = ctypes.c_uint

# XS_EnumSensorPID
# Returns the sensor PRODUCT ID at the indexed location of the enumerated sensors list.  The index is zero based.
# SENSORPID XS_EnumSensorPID(uint32_t nEnumIndex);
XS_EnumSensorPID = libXSC.XS_EnumSensorPID
XS_EnumSensorPID.argtypes = [ctypes.c_uint]
XS_EnumSensorPID.restype = ctypes.c_ulonglong


# XS_GetSerialFromPID
# Retrieve a sensor's 4 digit serial number.
# uint16_t XS_GetSerialFromPID(SENSORPID spid);
XS_GetSerialFromPID = libXSC.XS_GetSerialFromPID
XS_GetSerialFromPID.argtypes = [ctypes.c_ulonglong]
XS_GetSerialFromPID.restype = ctypes.c_ushort


# XS_GetSensorDimensions
# Retrieves the sensor's row and column counts
# XBOOL XS_GetSensorDimensions(SENSORPID spid, uint16_t& nRows, uint16_t& nColumns)
XS_GetSensorDimensions = libXSC.XS_GetSensorDimensions
XS_GetSensorDimensions.argtypes = [ctypes.c_ulonglong, ctypes.c_void_p, ctypes.c_void_p]
XS_GetSensorDimensions.restype = ctypes.c_ubyte

# XS_GetSensorName
# Returns the display name of the sensor. Example: HX210.11.31.M9-LF S0002
# The string is made of 16 bit wchar_t characters (UTF-16/UCS-2) which is null terminated.
# If pBuffer is 0 or NULL, the length of the required buffer (in wchar_t count) is calculated
# and returned in bufferSize.
# If pBuffer is not null, then bufferSize should be the length of the buffer in wchar_t.
#
# XBOOL XS_GetSensorName(SENSORPID spid, uint32_t& bufferSize, wchar_t* pBuffer = NULL);
XS_GetSensorName = libXSC.XS_GetSensorName
XS_GetSensorName.argtypes = [ctypes.c_ulonglong, ctypes.c_void_p, ctypes.c_void_p]
XS_GetSensorName.restype = ctypes.c_ubyte

# XS_GetSensorNameUTF8
# Returns the display name of the sensor. Example: HX210.11.31.M9-LF S0002
# The string is encoded in UTF8made.
# If pBuffer is 0 or NULL, the length of the required buffer (in bytes count) is calculated
# and returned in bufferSize.
# If pBuffer is not null, then bufferSize should be the length of the buffer in bytes.
#
# XBOOL XS_GetSensorNameUTF8(SENSORPID spid, uint32_t& bufferSize, char* pBuffer = NULL);
XS_GetSensorNameUTF8 = libXSC.XS_GetSensorNameUTF8
XS_GetSensorNameUTF8.argtypes = [ctypes.c_ulonglong, ctypes.c_void_p, ctypes.c_void_p]
XS_GetSensorNameUTF8.restype = ctypes.c_ubyte


# XS_IsX4Sensor
# Is this an X4 sensor?
# XBOOL XS_IsX4Sensor(SENSORPID spid);
XS_IsX4Sensor = libXSC.XS_IsX4Sensor
XS_IsX4Sensor.argtypes = [ctypes.c_ulonglong]
XS_IsX4Sensor.restype = ctypes.c_ubyte

# XS_IsX4FootSensor
# Sets bFootSensor to xTRUE if the sensor is an X4 foot sensor. Sets bLeftFoot to xTRUE if its a left foot sensor, and xFALSE for right sensors
# XBOOL XS_IsX4FootSensor(SENSORPID spid, XBOOL& bFootSensor, XBOOL& bLeftFoot);
XS_IsX4FootSensor = libXSC.XS_IsX4FootSensor
XS_IsX4FootSensor.argtypes = [ctypes.c_ulonglong, ctypes.c_void_p, ctypes.c_void_p]
XS_IsX4FootSensor.restype = ctypes.c_ubyte


# ===========================================================================
#	Calibration file management
# ===========================================================================

# XS_SetCalibrationFolder
# When the DLL is provided with a folder for caching calibration files, it will automatically
# manage downloading and selection of an appropriate calibration file.
# While enabled, the other calibration file functions are not enabled.
#
# Typically this is the best option for managing calibration files
#
# Alternatively you may use the following functions for direct management
# of a sensor's calibration files:
# XS_DownloadCalibrations; XS_GetCalibrationName; XS_GetCalibrationInfo; XS_GetCalibrationInfoEx
# XBOOL XS_SetCalibrationFolder(const wchar_t* szCalibrationFolder);
XS_SetCalibrationFolder = libXSC.XS_SetCalibrationFolder
XS_SetCalibrationFolder.argtypes = [ctypes.c_wchar_p]
XS_SetCalibrationFolder.restype = ctypes.c_uint

# XS_SetCalibrationFolderUTF8
# When the DLL is provided with a folder for caching calibration files, it will automatically
# manage downloading and selection of an appropriate calibration file.
# While enabled, the other calibration file functions are not enabled.
#
# Typically this is the best option for managing calibration files
#
# Alternatively you may use the following functions for direct management
# of a sensor's calibration files:
# XS_DownloadCalibrations; XS_GetCalibrationName; XS_GetCalibrationInfo; XS_GetCalibrationInfoEx
# XBOOL XS_SetCalibrationFolder(const wchar_t* szCalibrationFolder);
XS_SetCalibrationFolderUTF8 = libXSC.XS_SetCalibrationFolderUTF8
XS_SetCalibrationFolderUTF8.argtypes = [ctypes.c_char_p]
XS_SetCalibrationFolderUTF8.restype = ctypes.c_uint


# XS_DownloadCalibrations
# Downloads the calibration files stored on the target sensor and saves them to a folder.  Returns number of files downloaded.
# There may be 0, 1 or more calibration files on the sensor.  Usually if there are more then 1, then each file represents
# a different calibrated pressure range.
# uint32_t XS_DownloadCalibrations(SENSORPID spid, const wchar_t* szCalibrationFolder);
XS_DownloadCalibrations = libXSC.XS_DownloadCalibrations
XS_DownloadCalibrations.argtypes = [ctypes.c_ulonglong, ctypes.c_wchar_p]
XS_DownloadCalibrations.restype = ctypes.c_uint

# XS_DownloadCalibrationsUTF8
# Downloads the calibration files stored on the target sensor and saves them to a folder.  Returns number of files downloaded.
# There may be 0, 1 or more calibration files on the sensor.  Usually if there are more then 1, then each file represents
# a different calibrated pressure range.
# uint32_t XS_DownloadCalibrations(SENSORPID spid, const char* szCalibrationFolder);
XS_DownloadCalibrationsUTF8 = libXSC.XS_DownloadCalibrationsUTF8
XS_DownloadCalibrationsUTF8.argtypes = [ctypes.c_ulonglong, ctypes.c_char_p]
XS_DownloadCalibrationsUTF8.restype = ctypes.c_uint

# XS_GetCalibrationName
# After calling XS_DownloadCalibrations(), call this function to retrieve the name of the downloaded calibration file.
# If pBuffer is None, the size of the required buffer (in bytes) is calculated and returned in dwBufferSize.
# 'nCalIndex' is a zero based index.
# NOTE: this function only applies to the XS_DownloadCalibrations() call.  It does not work with XS_AddSensorToConfig_AutoCal().
# XBOOL XS_GetCalibrationName(uint32_t nCalIndex, uint32_t& dwBufferSize, wchar_t* pBuffer = NULL);
XS_GetCalibrationName = libXSC.XS_GetCalibrationName
XS_GetCalibrationName.argtypes = [ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]
XS_GetCalibrationName.restype = ctypes.c_ubyte

# XS_GetCalibrationNameUTF8
# After calling XS_DownloadCalibrationsUTF8(), call this function to retrieve the name of the downloaded calibration file.
# If pBuffer is None, the size of the required buffer (in bytes) is calculated and returned in dwBufferSize.
# 'nCalIndex' is a zero based index.
# NOTE: this function only applies to the XS_DownloadCalibrationsUTF8() call.  It does not work with XS_AddSensorToConfig_AutoCal().
# XBOOL XS_GetCalibrationNameUTF8(uint32_t nCalIndex, uint32_t& dwBufferSize, char* pBuffer = NULL);
XS_GetCalibrationNameUTF8 = libXSC.XS_GetCalibrationNameUTF8
XS_GetCalibrationNameUTF8.argtypes = [ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]
XS_GetCalibrationNameUTF8.restype = ctypes.c_ubyte

# XS_GetCalibrationInfo
# Scans the calibration file, and returns the maximum pressure (in the provided pressure units - see EPressureUnit)
# szCalibrationFile is the full path to the cal file on disk.  eg: c:\\CalFiles\\MyCalFile.xsc
# XBOOL XS_GetCalibrationInfo(const wchar_t* szCalibrationFile, uint8_t nPressureUnits, float& nMinPressure, float& nMaxPressure);
XS_GetCalibrationInfo = libXSC.XS_GetCalibrationInfo
XS_GetCalibrationInfo.argtypes = [ctypes.c_wchar_p, ctypes.c_ubyte, ctypes.c_void_p, ctypes.c_void_p]
XS_GetCalibrationInfo.restype = ctypes.c_ubyte

# XS_GetCalibrationInfoUTF8
# Scans the calibration file, and returns the maximum pressure (in the provided pressure units - see EPressureUnit)
# szCalibrationFile is the full path to the cal file on disk.  eg: c:\\CalFiles\\MyCalFile.xsc
# XBOOL XS_GetCalibrationInfoUTF8(const char* szCalibrationFile, uint8_t nPressureUnits, float& nMinPressure, float& nMaxPressure);
XS_GetCalibrationInfoUTF8 = libXSC.XS_GetCalibrationInfoUTF8
XS_GetCalibrationInfoUTF8.argtypes = [ctypes.c_char_p, ctypes.c_ubyte, ctypes.c_void_p, ctypes.c_void_p]
XS_GetCalibrationInfoUTF8.restype = ctypes.c_ubyte


# XS_GetCalibrationInfoEx
# Retrieve the SENSORPID from this calibration file
# szCalibrationFile is the full path to the cal file on disk.  eg: c:\\CalFiles\\MyCalFile.xsc
# XBOOL XS_GetCalibrationInfoEx(const wchar_t* szCalibrationFile, SENSORPID& spid);
XS_GetCalibrationInfoEx = libXSC.XS_GetCalibrationInfoEx
XS_GetCalibrationInfoEx.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p]
XS_GetCalibrationInfoEx.restype = ctypes.c_ubyte

# XS_GetCalibrationInfoExUTF8
# Retrieve the SENSORPID from this calibration file
# szCalibrationFile is the full path to the cal file on disk.  eg: c:\\CalFiles\\MyCalFile.xsc
# XBOOL XS_GetCalibrationInfoExUTF8(const char* szCalibrationFile, SENSORPID& spid);
XS_GetCalibrationInfoExUTF8 = libXSC.XS_GetCalibrationInfoExUTF8
XS_GetCalibrationInfoExUTF8.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
XS_GetCalibrationInfoExUTF8.restype = ctypes.c_ubyte


# ===========================================================================
#	AUTOMATIC Sensor Configuration
#
#	These functions simplify the process of configuring any connected sensors.
# ===========================================================================

# XS_AutoConfig
# creates a configuration using all sensors attached to the system.  Downloads any calibration files into memory and uses them.
# Please note that while this is the simplest way to configure the sensors, it is also the slowest because the calibration download takes a fair bit of time.
# XBOOL XS_AutoConfig(EPressureUnits eUnits, float nTargetPressure);
XS_AutoConfig = libXSC.XS_AutoConfig
XS_AutoConfig.argtypes = [ctypes.c_ubyte, ctypes.c_float]
XS_AutoConfig.restype = ctypes.c_ubyte

# XS_AutoConfigXSN
# Similar to XS_AutoConfig(), but also creates a standalone XSN session file.
# The szXSNFile path and file name must be fully specified. eg: "c:\MySessions\Test.xsn".
# XBOOL XS_AutoConfigXSN(const wchar_t* szXSNFile, uint8_t nPressureUnits = ePRESUNIT_MMHG, float nTargetPressure = -1.0f);
XS_AutoConfigXSN = libXSC.XS_AutoConfigXSN
XS_AutoConfigXSN.argtypes = [ctypes.c_wchar_p, ctypes.c_ubyte, ctypes.c_float]
XS_AutoConfigXSN.restype = ctypes.c_ubyte

# XS_AutoConfigXSNUTF8
# Similar to XS_AutoConfig(), but also creates a standalone XSN session file.
# The szXSNFile path and file name must be fully specified. eg: "c:\MySessions\Test.xsn".
# XBOOL XS_AutoConfigXSNUTF8(const char* szXSNFile, uint8_t nPressureUnits = ePRESUNIT_MMHG, float nTargetPressure = -1.0f);
XS_AutoConfigXSNUTF8 = libXSC.XS_AutoConfigXSNUTF8
XS_AutoConfigXSNUTF8.argtypes = [ctypes.c_char_p, ctypes.c_ubyte, ctypes.c_float]
XS_AutoConfigXSNUTF8.restype = ctypes.c_ubyte


# XS_AutoConfigByDefault
# creates a configuration using all sensors attached to the system.  Downloads any calibration files into memory and uses them.
# Please note that while this is the simplest way to configure the sensors, it is also the slowest because the calibration download takes a fair bit of time.
# XBOOL XS_AutoConfigByDefault();
XS_AutoConfigByDefault = libXSC.XS_AutoConfigByDefault
XS_AutoConfigByDefault.restype = ctypes.c_ubyte

# XS_AutoConfigByDefaultXSN
# creates a configuration using all sensors attached to the system.  Downloads any calibration files into memory and uses them.
# Constructs an XSN file to store the frames.
# Please note that while this is the simplest way to configure the sensors, it is also the slowest because the calibration download takes a fair bit of time.
# XBOOL XS_AutoConfigByDefault(const wchar_t* szXSNFile);
XS_AutoConfigByDefaultXSN = libXSC.XS_AutoConfigByDefaultXSN
XS_AutoConfigByDefaultXSN.argtypes = [ctypes.c_wchar_p]
XS_AutoConfigByDefaultXSN.restype = ctypes.c_ubyte

# XS_AutoConfigByDefaultXSN
# creates a configuration using all sensors attached to the system.  Downloads any calibration files into memory and uses them.
# Constructs an XSN file to store the frames.
# Please note that while this is the simplest way to configure the sensors, it is also the slowest because the calibration download takes a fair bit of time.
# XBOOL XS_AutoConfigByDefaultXSNUTF8(const char* szXSNFile);
XS_AutoConfigByDefaultXSNUTF8 = libXSC.XS_AutoConfigByDefaultXSNUTF8
XS_AutoConfigByDefaultXSNUTF8.argtypes = [ctypes.c_char_p]
XS_AutoConfigByDefaultXSNUTF8.restype = ctypes.c_ubyte

# XS_AutoConfig_SingleSensor
# Wraps all of the enumeration and configuration into a single call.
# Optionally provide a path to a calibration file to override any calibration downloads.
# ie: XS_AutoConfig_SingleSensor(L"d:\\MyCalFiles\\PX100363605_20121022_1151.xsc");
# This only works if there is a single sensor present.
# XBOOL XS_AutoConfig_SingleSensor(const wchar_t* szCalFile=NULL);
XS_AutoConfig_SingleSensor = libXSC.XS_AutoConfig_SingleSensor
XS_AutoConfig_SingleSensor.argtypes = [ctypes.c_wchar_p]
XS_AutoConfig_SingleSensor.restype = ctypes.c_ubyte

# XS_AutoConfig_SingleSensorUTF8
# Wraps all of the enumeration and configuration into a single call.
# Optionally provide a path to a calibration file to override any calibration downloads.
# ie: XS_AutoConfig_SingleSensorUTF8(L"d:\\MyCalFiles\\PX100363605_20121022_1151.xsc");
# This only works if there is a single sensor present.
# XBOOL XS_AutoConfig_SingleSensorUTF8(const char* szCalFile=NULL);
XS_AutoConfig_SingleSensorUTF8 = libXSC.XS_AutoConfig_SingleSensorUTF8
XS_AutoConfig_SingleSensorUTF8.argtypes = [ctypes.c_char_p]
XS_AutoConfig_SingleSensorUTF8.restype = ctypes.c_ubyte

# XBOOL XS_AutoConfig_SingleSensorXSN(const wchar_t* szXSNFile, const wchar_t* szCalFile=NULL);
XS_AutoConfig_SingleSensorXSN = libXSC.XS_AutoConfig_SingleSensorXSN
XS_AutoConfig_SingleSensorXSN.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
XS_AutoConfig_SingleSensorXSN.restype = ctypes.c_ubyte

# XBOOL XS_AutoConfig_SingleSensorXSNUTF8(const wchar_t* szXSNFile, const char* szCalFile=NULL);
XS_AutoConfig_SingleSensorXSNUTF8 = libXSC.XS_AutoConfig_SingleSensorXSNUTF8
XS_AutoConfig_SingleSensorXSNUTF8.argtypes = [ctypes.c_wchar_p, ctypes.c_char_p]
XS_AutoConfig_SingleSensorXSNUTF8.restype = ctypes.c_ubyte

# ===========================================================================
#	MANUAL Sensor Configuration
#
#	These functions give better control over the configuration of any connected
#	sensors.
# ===========================================================================

# XS_NewSensorConfig
# Prepares the DLL to create a configuration of sensors.  Remove any existing configured sensors.
# XBOOL XS_NewSensorConfig();
XS_NewSensorConfig = libXSC.XS_NewSensorConfig
XS_NewSensorConfig.restype = ctypes.c_ubyte

# XS_NewSensorConfigXSN
# Similar to XS_NewSensorConfig(), but also creates a standalone XSN session file.
# The szXSNFile path and file name must be fully specified. eg: "c:\MySessions\Test.xsn".
# XBOOL XS_NewSensorConfigXSN(const wchar_t* szXSNFile);
XS_NewSensorConfigXSN = libXSC.XS_NewSensorConfigXSN
XS_NewSensorConfigXSN.argtypes = [ctypes.c_wchar_p]
XS_NewSensorConfigXSN.restype = ctypes.c_ubyte

# XS_NewSensorConfigXSNUTF8
# Similar to XS_NewSensorConfig(), but also creates a standalone XSN session file.
# The szXSNFile path and file name must be fully specified. eg: "c:\MySessions\Test.xsn".
# XBOOL XS_NewSensorConfigXSNUTF8(const char* szXSNFile);
XS_NewSensorConfigXSNUTF8 = libXSC.XS_NewSensorConfigXSNUTF8
XS_NewSensorConfigXSNUTF8.argtypes = [ctypes.c_char_p]
XS_NewSensorConfigXSNUTF8.restype = ctypes.c_ubyte

# XS_AddSensorToConfig
# Adds a sensor to the sensor configuration.  Sensors in the configuration are sampled when XS_Sample() is called.
# A calibration file can be specified here.  If szCalibrationFile is 0, then only raw data is collected.
# All sensors in the configuration must have calibration files, otherwise only raw values are collected.
# XBOOL XS_AddSensorToConfig(SENSORPID spid, const wchar_t* szCalibrationFile);
XS_AddSensorToConfig = libXSC.XS_AddSensorToConfig
XS_AddSensorToConfig.argtypes = [ctypes.c_ulonglong, ctypes.c_wchar_p]
XS_AddSensorToConfig.restype = ctypes.c_ubyte

# XS_AddSensorToConfigUTF8
# Adds a sensor to the sensor configuration.  Sensors in the configuration are sampled when XS_Sample() is called.
# A calibration file can be specified here.  If szCalibrationFile is 0, then only raw data is collected.
# All sensors in the configuration must have calibration files, otherwise only raw values are collected.
# XBOOL XS_AddSensorToConfigUTF8(SENSORPID spid, const char* szCalibrationFile);
XS_AddSensorToConfigUTF8 = libXSC.XS_AddSensorToConfigUTF8
XS_AddSensorToConfigUTF8.argtypes = [ctypes.c_ulonglong, ctypes.c_char_p]
XS_AddSensorToConfigUTF8.restype = ctypes.c_ubyte


# XS_AddSensorToConfig_AutoCalByDefault
# Adds a sensor to the sensor configuration.  Sensors in the configuration are sampled when XS_Sample() is called.
# Attempts to download a calibration file from the sensor and use it.
# If nPressureUnits is raw, then it uses the first calibration file it finds, otherwise it attempts to match the desired maximum pressure
# Note: Downloading can be a bit slow.
# XBOOL XS_AddSensorToConfig_AutoCalByDefault(SENSORPID spid);
XS_AddSensorToConfig_AutoCalByDefault = libXSC.XS_AddSensorToConfig_AutoCalByDefault
XS_AddSensorToConfig_AutoCalByDefault.argtypes = [ctypes.c_ulonglong]
XS_AddSensorToConfig_AutoCalByDefault.restype = ctypes.c_ubyte

# XS_AddSensorToConfig_AutoCal
# see XS_AddSensorToConfig_AutoCalByDefault
# XBOOL XS_AddSensorToConfig_AutoCal(SENSORPID spid, uint8_t nPressureUnits = ePRESUNIT_MMHG, float nTargetMaxPressure = -1.0f);
XS_AddSensorToConfig_AutoCal = libXSC.XS_AddSensorToConfig_AutoCal
XS_AddSensorToConfig_AutoCal.argtypes = [ctypes.c_ulonglong, ctypes.c_ubyte, ctypes.c_float]
XS_AddSensorToConfig_AutoCal.restype = ctypes.c_ubyte

# XS_ConfigComplete
# When finished adding sensors to the configuration, call this function to initialize it and prepare for calling XS_OpenConnection()
# XBOOL XS_ConfigComplete();
XS_ConfigComplete = libXSC.XS_ConfigComplete
XS_ConfigComplete.restype = ctypes.c_ubyte

# XS_HasConfig
# Returns xTRUE if the DLL has a sensor configuration
# XBOOL XS_HasConfig();
XS_HasConfig = libXSC.XS_HasConfig
XS_HasConfig.restype = ctypes.c_ubyte


# XS_ReleaseConfig
# Closes any open connection and releases the configuration (including any XSN file).
# Subsequent calls to XS_OpenConnection will fail until a new config is created.
# XBOOL XS_ReleaseConfig();
XS_ReleaseConfig = libXSC.XS_ReleaseConfig
XS_ReleaseConfig.restype = ctypes.c_ubyte


# ===========================================================================
#	Sensor Configuration Information
# ===========================================================================

# XS_ConfigSensorPID
# Returns the sensor PRODUCT ID at the indexed location of the configured sensors list.  The index is zero based.
# Call XS_NewSensorConfig+XS_AddSensorToConfig+XS_ConfigComplete or XS_AutoConfigByDefault() before calling this function.
# SENSORPID XS_ConfigSensorPID(uint32_t nConfigIndex);
XS_ConfigSensorPID = libXSC.XS_ConfigSensorPID
XS_ConfigSensorPID.argtypes = [ctypes.c_uint]
XS_ConfigSensorPID.restype = ctypes.c_ulonglong


# XS_ConfigSensorCount
# returns the number of configured sensors
# uint32_t XS_ConfigSensorCount();
XS_ConfigSensorCount = libXSC.XS_ConfigSensorCount
XS_ConfigSensorCount.restype = ctypes.c_uint


# XS_IsCalibrationConfigured
# Returns 1 if the configuration is setup for calibrated data.
# XBOOL XS_IsCalibrationConfigured();
XS_IsCalibrationConfigured = libXSC.XS_IsCalibrationConfigured
XS_IsCalibrationConfigured.restype = ctypes.c_ubyte


# XS_GetConfigInfo
# After the configuration is complete, call this to check the pressure range of the sensor.
# nPressureUnits - the pressure units in which the minimum and maximum pressures are returned. (See EPressureUnits below)
# If operating in RAW mode (i.e.: no calibration file specified), then nPressureUnits is ignored.
# XBOOL XS_GetConfigInfo(uint8_t nPressureUnits, float& nMinPressure, float& nMaxPressure);
XS_GetConfigInfo = libXSC.XS_GetConfigInfo
XS_GetConfigInfo.argtypes = [ctypes.c_ubyte, ctypes.c_void_p, ctypes.c_void_p]
XS_GetConfigInfo.restype = ctypes.c_ubyte


# XS_GetSenselDims
# returns a single sensel's physical dimensions in centimetres. Note this only works once a sensor configuration is via XS_AutoConfigByDefault or XS_ConfigComplete
# XBOOL XS_GetSenselDims(SENSORPID spid, float& nWidthCM, float& nHeightCM);
XS_GetSenselDims = libXSC.XS_GetSenselDims
XS_GetSenselDims.argtypes = [ctypes.c_ulonglong, ctypes.c_void_p, ctypes.c_void_p]
XS_GetSenselDims.restype = ctypes.c_ubyte


# ===========================================================================
#	Other Settings
# ===========================================================================

# XS_SetPressureUnit
# Sets the calibrated data's pressure units.  This can be changed at any time.
# Pass in a value of type EPressureUnit
# void XS_SetPressureUnit(uint8_t PressureUnit);
XS_SetPressureUnit = libXSC.XS_SetPressureUnit
XS_SetPressureUnit.argtypes = [ctypes.c_ubyte]
# has no return value XS_SetPressureUnit.restype = ctypes.c_ubyte


# XS_GetPressureUnit
# Returns the current pressure units (see EPressureUnits).
# uint8_t XS_GetPressureUnit();
XS_GetPressureUnit = libXSC.XS_GetPressureUnit
XS_GetPressureUnit.restype = ctypes.c_ubyte


# XS_SetReadTimeout
# Sets the sample function's timeout period (in seconds).
# 5 seconds is default
# void XS_SetReadTimeout(uint32_t TimeoutSeconds);
XS_SetReadTimeout = libXSC.XS_SetReadTimeout
XS_SetReadTimeout.argtypes = [ctypes.c_uint]
# has no return value XS_SetReadTimeout.restype = ctypes.c_ubyte


# XS_GetReadTimeout
# returns the sample timeout period in seconds
# uint32_t XS_GetReadTimeout();
XS_GetReadTimeout = libXSC.XS_GetReadTimeout
XS_GetReadTimeout.restype = ctypes.c_uint


# XS_SetOverlapMode
# if the sensors are physically overlapped, ensure this mode is on to avoid image distortion
# void XS_SetOverlapMode(XBOOL bOverlap);
XS_SetOverlapMode = libXSC.XS_SetOverlapMode
XS_SetOverlapMode.argtypes = [ctypes.c_ubyte]
# has no return value XS_SetOverlapMode.restype = ctypes.c_ubyte

# XS_GetOverlapMode
# returns true (non-zero) if overlap mode is on, false otherwise.  This is on by default.
# XBOOL XS_GetOverlapMode();
XS_GetOverlapMode = libXSC.XS_GetOverlapMode
XS_GetOverlapMode.restype = ctypes.c_ubyte


# XS_SetAllowWireless
# allows use of the X3 wireless series
XS_SetAllowWireless = libXSC.XS_SetAllowWireless
XS_SetAllowWireless.argtypes = [ctypes.c_ubyte]
# has no return value

# XS_GetAllowWireless
# returns 1 if the DLL is allowed to scan for X3 wireless sensors, or 0 otherwise
XS_GetAllowWireless = libXSC.XS_GetAllowWireless
XS_GetAllowWireless.restype = ctypes.c_ubyte


# XS_SetAllowX4
# allow the DLL to find X4 sensors that are connected by USB
XS_SetAllowX4 = libXSC.XS_SetAllowX4
XS_SetAllowX4.argtypes = [ctypes.c_ubyte]
# has no return value

# XS_GetAllowX4
# returns 1 if the DLL is allowed to scan for X4 wired sensors, or 0 otherwise
XS_GetAllowX4 = libXSC.XS_GetAllowX4
XS_GetAllowX4.restype = ctypes.c_ubyte


# XS_SetAllowX4Wireless
# allow the DLL to find X4 sensors that are connected by Bluetooth
XS_SetAllowX4Wireless = libXSC.XS_SetAllowX4Wireless
XS_SetAllowX4Wireless.argtypes = [ctypes.c_ubyte]
# has no return value

# XS_GetAllowX4Wireless
# returns 1 if the DLL is allowed to scan for X4 Bluetooth sensors, or 0 otherwise
XS_GetAllowX4Wireless = libXSC.XS_GetAllowX4Wireless
XS_GetAllowX4Wireless.restype = ctypes.c_ubyte


# XS_SetX4Mode8Bit
# Place the X4 in 8 bit mode - This can improve the reliability of Bluetooth transmission speeds. Has no impact on actual recording speed.
# Pass in 1 to enable 8 bit mode, 0 to restore the normal 16 bit mode
XS_SetX4Mode8Bit = libXSC.XS_SetX4Mode8Bit
XS_SetX4Mode8Bit.argtypes = [ctypes.c_ubyte]
# has no return value

# XS_GetX4Mode8Bit
# returns 1 if X4 8 bit mode is enabled, 0 if 16 bit is enabled
XS_GetX4Mode8Bit = libXSC.XS_GetX4Mode8Bit
XS_GetX4Mode8Bit.restype = ctypes.c_ubyte

# XS_HasHardwareIMU
# returns 1 if the sensor supports IMU collection
# XBOOL XS_HasHardwareIMU(SENSORPID spid);
XS_HasHardwareIMU = libXSC.XS_HasHardwareIMU;
XS_HasHardwareIMU.argtypes = [ctypes.c_ulonglong]
XS_HasHardwareIMU.restype = ctypes.c_ubyte

# XS_SetEnableIMU
# allow the DLL to enable IMU hardware when present on an X4 sensor
# void XS_SetEnableIMU(XBOOL bEnable);
XS_SetEnableIMU = libXSC.XS_SetEnableIMU;
XS_SetEnableIMU.argtypes = [ctypes.c_ubyte]

# XS_GetEnableIMU
# returns true (non-zero) if IMU enable flag is set. (The flag maybe set regardless of actual IMU support.)
# XBOOL XS_GetEnableIMU();
XS_GetEnableIMU = libXSC.XS_GetEnableIMU
XS_GetEnableIMU.restype = ctypes.c_ubyte


# XS_SetStreamingMode
# If you are sampling < 10 Hz, set this mode to false, otherwise set to true for better sample rates
# void XS_SetStreamingMode(XBOOL bStreaming);
XS_SetStreamingMode = libXSC.XS_SetStreamingMode
XS_SetStreamingMode.argtypes = [ctypes.c_ubyte]
# has no return value XS_SetStreamingMode.restype = ctypes.c_ubyte

# XS_GetStreamingMode
# returns true (non-zero) if streaming mode is on, false otherwise.  This is off by default.
# XBOOL XS_GetStreamingMode();
XS_GetStreamingMode = libXSC.XS_GetStreamingMode
XS_GetStreamingMode.restype = ctypes.c_ubyte


# XS_SetSampleAverageCount
# Set the number of readings the hardware will perform on each sensel.
# Valid numbers are 1, 2, 4, 8 and 16
#
# This averaging occurs within the sensor's DPS hardware. Higher cycles lead to slower
# frame rates, but may produce more accurate readings.
#
# X4 sensors can only run at 4 and 8 cycles. X4 foot sensors run fastest with 4 cycles.
#
# This value can only be set before calling any of the XS_AutoConfig* functions, or XS_ConfigComplete()
# Typically you don't need to set this as the sensor is normally programmed with an expected default.
# void XS_SetSampleAverageCount(uint16_t nCount);
XS_SetSampleAverageCount = libXSC.XS_SetSampleAverageCount
XS_SetSampleAverageCount.argtypes = [ctypes.c_ushort]

# XS_GetSampleAverageCount
# returns the number of readings the hardware will perform on each sensel.  Each reading is
# averaged together.  Default is 1 which means no averaging.  Hardware supports: 1,2,4,8,16 samples being averaged.
# uint16_t XS_GetSampleAverageCount();
XS_GetSampleAverageCount = libXSC.XS_GetSampleAverageCount
XS_GetSampleAverageCount.restype = ctypes.c_ushort


# C functions not presently supported (2021-03-12)
# XS_AllocPressureBuffer
# XS_ReleasePressureBuffer
# XS_AllocRawBuffer
# XS_ReleaseRawBuffer


# ===========================================================================
#	Connection management
# ===========================================================================

# XS_OpenConnection
# opens the sensors in the sample configuration and readies them for sampling
# Call this only after a call to XS_ConfigComplete() or XS_AutoConfig*()
#
# nThreadedFramesPerMinute
#	- When using the DLL in threaded mode (ie: XS_InitLibrary(TRUE)),
#    this specifies the target frame rate. eg: 10 Hz = 600 FPM
#    Actual rate may be slower depending on the sensor configuration and
#    the PC's USB subsystem. This field is ignored when XS_InitLibrary(FALSE)
#	  is called.
#XBOOL XS_OpenConnection(uint32_t nThreadedFramesPerMinute=0);
XS_OpenConnection = libXSC.XS_OpenConnection
XS_OpenConnection.argtypes = [ctypes.c_uint]
XS_OpenConnection.restype = ctypes.c_ubyte


# XS_IsConnectionOpen
# returns 1 if the connection is open
# XBOOL XS_IsConnectionOpen();
XS_IsConnectionOpen = libXSC.XS_IsConnectionOpen
XS_IsConnectionOpen.restype = ctypes.c_ubyte

# XS_IsConnectionThreaded
# returns 1 if the connection is open and the connection is running in an asynchronous threaded mode.
# XBOOL XS_IsConnectionThreaded();
XS_IsConnectionThreaded = libXSC.XS_IsConnectionThreaded
XS_IsConnectionThreaded.restype = ctypes.c_ubyte


# XS_CloseConnection
# closes the connection - this releases the sensors and allows other applications to talk to them.
# XBOOL XS_CloseConnection();
XS_CloseConnection = libXSC.XS_CloseConnection
XS_CloseConnection.restype = ctypes.c_ubyte


# ===========================================================================
#	Sampling functions
# ===========================================================================

# XS_GetNoiseThreshold
# Returns the threshold below which pressure is zeroed.
# float XS_GetNoiseThreshold();
XS_GetNoiseThreshold = libXSC.XS_GetNoiseThreshold
XS_GetNoiseThreshold.restype = ctypes.c_float

# XS_SetNoiseThreshold
# sets a pressure threshold. Any readings below this threshold are zeroed.
# XBOOL XS_SetNoiseThreshold(float nThreshold);
XS_SetNoiseThreshold = libXSC.XS_SetNoiseThreshold
XS_SetNoiseThreshold.argtypes = [ctypes.c_float]
XS_SetNoiseThreshold.restype = ctypes.c_ubyte


# XS_Sample
# Ask the sensor(s) to record a sample.
# Returns 1 if a sample is collected, 0 otherwise
# XBOOL XS_Sample();
XS_Sample = libXSC.XS_Sample
XS_Sample.restype = ctypes.c_ubyte

# XS_GetSampleTimestampUTC
# Fetch the timestamp components (UTC time). month (1-12), day (1-31). Hour is (0-23), minute and second (0-59), millisecond (0-999)
# XBOOL XS_GetSampleTimestampUTC(uint16_t& year, uint8_t& month, uint8_t& day, uint8_t& hour, uint8_t& minute, uint8_t& second, uint16_t& millisecond);
XS_GetSampleTimestampUTC = libXSC.XS_GetSampleTimestampUTC
XS_GetSampleTimestampUTC.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
XS_GetSampleTimestampUTC.restype = ctypes.c_ubyte

# XS_GetSampleTimestampExUTC
# includes microseconds when supported by the sensor hardware. This version allows conversion of the timestamp to the local timezone.
# XBOOL XS_GetSampleTimestampExUTC(
#	uint16_t& year, uint8_t& month, uint8_t& day, 
#	uint8_t& hour, uint8_t& minute, uint8_t& second, uint16_t& millisecond, uint16_t& microsecond, bool bAsLocalTime);
XS_GetSampleTimestampExUTC = libXSC.XS_GetSampleTimestampExUTC
XS_GetSampleTimestampExUTC.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ubyte]
XS_GetSampleTimestampExUTC.restype = ctypes.c_ubyte

# C functions not presently supported (2021-03-12)
# XBOOL XS_GetSampleTimeUTC(SYSTEMTIME& tTime);

# XS_GetPressure
# Retrieves the sensor sample data for a single sensor.
# The expected pData buffer format is rows * columns * sizeof(uint16_t), where rows and columns are the dimensions of the sensor.
# XBOOL XS_GetPressure(SENSORPID spid, float* pData);
XS_GetPressure = libXSC.XS_GetPressure
XS_GetPressure.argtypes = [ctypes.c_ulonglong, ctypes.c_void_p]
XS_GetPressure.restype = ctypes.c_ubyte

# XS_GetPressureSafe
# This version takes a preallocated buffer of floats (32 bit) whose size is dataSize.
# dataSize is the number of elements in the data[] array
# XBOOL XS_GetPressureSafe(SENSORPID spid, uint32_t dataSize, float data[]);
XS_GetPressureSafe = libXSC.XS_GetPressureSafe
XS_GetPressureSafe.argtypes = [ctypes.c_ulonglong, ctypes.c_uint, ctypes.c_void_p]
XS_GetPressureSafe.restype = ctypes.c_ubyte

# XS_GetRaw
# Retrieves the raw sample data for a single sensor.
# The expected pData buffer format is rows * columns * sizeof(ushort), where rows and columns are the dimensions of the sensor.
# XBOOL XS_GetRaw(SENSORPID spid, uint16_t* pData);
XS_GetRaw = libXSC.XS_GetRaw
XS_GetRaw.argtypes = [ctypes.c_ulonglong, ctypes.c_void_p]
XS_GetRaw.restype = ctypes.c_ubyte

# XS_GetRawSafe
# This version takes a preallocated buffer whose size is specified with dataSize.
# XBOOL XS_GetRawSafe(SENSORPID spid, uint32_t dataSize, uint16_t data[]);
# dataSize is the number of elements in the data[] array
XS_GetRawSafe = libXSC.XS_GetRawSafe
XS_GetRawSafe.argtypes = [ctypes.c_ulonglong, ctypes.c_uint, ctypes.c_void_p]
XS_GetRawSafe.restype = ctypes.c_ubyte

# XS_GetIMU
# XBOOL XS_GetIMU(
#	SENSORPID spid,
#	float& qx, float& qy, float& qz, float& qw,
#	float& ax, float& ay, float& az,
#	float& gx, float& gy, float& gz);
# Fetches the IMU data (if any) for the current Sample
XS_GetIMU = libXSC.XS_GetIMU
XS_GetIMU.argtypes = [ctypes.c_ulonglong, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
XS_GetIMU.restype = ctypes.c_ubyte

# XS_GetHardwareFrameState
# XBOOL XS_GetHardwareFrameState(SENSORPID spid, uint32_t& sequence, uint32_t& ticks);
# Retrieves the hardware frame header state. 'sequence' increments (and wrapsaround) for each frame. 'ticks' is milliseconds for X4
# returns xFALSE if there is no hardware state, or an error has occured
XS_GetHardwareFrameState = libXSC.XS_GetHardwareFrameState
XS_GetHardwareFrameState.argtypes = [ctypes.c_ulonglong, ctypes.c_void_p, ctypes.c_void_p]
XS_GetHardwareFrameState.restype = ctypes.c_ubyte


# XS_CenterOfPressure
# Computes the center of pressure (COP) and returns its column and row coordinates.
# Returns negative coordinates if there is a problem. Call XSN_GetLastErrorCode() if that occurs.
#
# The center of pressure calculation ignores pressure which is below the zero threshold.
# zeroThreshold is assumed to be in the same pressure units as the current settings.
#
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
# XBOOL XS_CenterOfPressure(SENSORPID spid, float zeroThreshold, float& column, float& row);
XS_CenterOfPressure = libXSC.XS_CenterOfPressure
XS_CenterOfPressure.argtypes = [ctypes.c_ulonglong, ctypes.c_float, ctypes.c_void_p, ctypes.c_void_p]
XS_CenterOfPressure.restype = ctypes.c_ubyte


# C functions not presently supported (2021-03-12)
# XS_GetDeadMap


# ===========================================================================
#	External Sync port triggers - X3 PRO HUB sensor only
# ===========================================================================

# C functions not presently supported (2021-03-12)
# XS_IsRecordTrigger_FirstFrameOnly
# XS_EnableRecordTrigger_FirstFrameOnly
# XS_IsRecordTrigger_EachFrame
# XS_EnableRecordTrigger_EachFrame

# ===========================================================================
# END OF FILE
# ===========================================================================
