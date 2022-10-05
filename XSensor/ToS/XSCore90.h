#pragma once

/* XSCore90.h -- interface of the 'XSCore90' sensor engine.
  
  Copyright (C) 2010-2022  XSENSOR Technology Corporation. All rights reserved.

  This software is provided 'as-is', without any express or implied
  warranty.  In no event will XSENSOR Technology Corporation be held liable
  for any damages arising from the use of this software.

*/

/*	
	------------------------------------------------------------------------------------
	INTRODUCTION

	The XSCore library is used to communicate with XSENSOR Technology sensors.

	The sensors are rectangular grids of pressure sensing cells, called sensels.

	Each sensel converts surface pressure into an electronic signal which is
	stored internally as a 16 bit integer. This raw value is then converted
	into a calibrated pressure reading using information from a "calibration" file.

	Each sensor holds one or more calibration files within its onboard memory.
	These files must be downloaded to the computer in order to be used by the DLL.
	Normally the DLL handles this automatically, however it is possible to take control
	of certain aspects of that process in order to speed up subsequent use of the DLL.

	The grid of calibrated pressure readings is called a "pressure map" or "pressure image".
	Each sensor has its own pressure map.

	The library offers these features:
	* Sensor Enumeration
	* Sensor pressure map sampling
	* Synchronous (non-threaded) vs Asynchronous (threaded) operation
	* Access to raw 16 uncalibrated readings or 32 bit floating point calibrated pressure
	* Direct access to the pressure map and the ability to create an XSENSOR session file (XSN)

	MAJOR MODES:

		The DLL has two main operating modes and two main ways of dealing with samples.
		The operating modes are synchronous (non-threaded) and asyconrounous (threaded).

		In the threaded mode, calling XS_OpenConnection() will start the recording at
		the target frame rate (if possible). Samples (or frames) are stored to the XSN
		file while this occurs. Calling XS_Sample() in this case simply fetches a copy
		of the current frame from the XSN file, which you can then examine with XS_GetPressure().  
		XS_Sample() does not block in threaded mode. You stop this sampling by calling XS_CloseConnection().  
		You can call XS_OpenConnection again to resume collection of frames to the same XSN file.

		In the non-threaded mode, calling XS_OpenConnection() just opens a connection to the sensors and it sits idling.  
		Calling XS_Sample() instructs the DLL to fetch a live sample. This blocks until the fetch is complete. The sample
		is automatically stored in the XSN file.  Basically its a polling method whose frame rate you control (within 
		limits of the sensor and the USB connection).

		The mode is specified in the call to XS_InitLibrary(). 
		(Be sure to call XS_ExitLibrary() when you're done with the DLL).
	------------------------------------------------------------------------------------
	QUICK USAGE

	The following code assumes a single sensor is connected to the computer.

	void Test()
	{
		XS_InitLibrary(xFALSE);

		// Automatically create a sensor configuration with all connected sensors, using PSI pressure units.

		if ( XS_AutoConfig(ePRESUNIT_PSI) && (XS_ConfigSensorCount() >= 1) )
		{
			SENSORPID mySensorID = XS_ConfigSensorPID(0); // fetch the ID of the first sensor
			
			uint16_t rows = 0, columns = 0;
			uint16_t year, millisecond;
			uint8_t month, day, hour, minute, second;

			// Fetch the row and column counts for the sensor
			XS_GetSensorDimensions(mySensorID, rows, columns);

			// Allocate a buffer for accessing the pressure values. Use this for multiple readings.
			float* pPressureMap = XS_AllocPressureBuffer(mySensorID); // test this as it might return NULL or 0
			
	
			// alternatively allocate your own memory. Just remember to free it later
			// alt1: float* pPressureMap = malloc(rows * columns * sizeof(float));
			// alt2: float* pPressureMap = new float[rows * columns];

			
			// We'll open/close the connection a few times.
			// This demonstrates that a sensor configuration can be open/closed multiple times.
			// No need to recreation the configuration each time.

			for(int nConnectionLoop = 0; nConnectionLoop < 3; nConnectionLoop++)
			{
				// open the connection to the sensor
				uint32_t framesPerMinute = 20 * 60; // 20 Hz X 60 seconds = 1200 frames per minute

				if ( (pPressureMap != NULL) && XS_OpenConnection(framesPerMinute) )
				{
					// take 4 sample readings - for demo purposes
					for(int nSample = 0; nSample < 4; nSample++)
					{
						if (XS_Sample() && XS_GetPressure(mySensorID, pPressureMap))
						{
							// usually you'll also want to fetch the timestamp
							XS_GetSampleTimestampUTC(year, month, day, hour, minute, second, millisecond);
						
							// Now you have a pressure map. Do something with it, or copy it somewhere ...
						
							// For demo purposes - simply interate over the map
							for(uint16_t row = 0; row < rows; row++)
							{
								for(uint16_t column = 0; column < columns; column++)
								{
									float pressure = pPressureMap[row * columns + column];

									// do something with the pressure value ...
								}
							}
						}
					} // next sample

					// done with the connection
					XS_CloseConnection();
				}
			} // next open/close connection pass for the current sensor configuration


			// release the buffer memory - otherwise you'll have a memory leak
			XS_ReleasePressureBuffer(pPressureMap);

			// alt1: if(pPressureMap != NULL) free(pPressureMap);
			// alt2: if(pPressureMap != NULL) { delete[] pPressureMap; }
		}

		XS_ExitLibrary();
	} // end Test()
*/

#include <stdint.h> // for uint8_t, uint16_t, uint32_t

// leave XSCORE_EXPORTS undefined to import the DLL via its lib
#ifndef XSCORE_EXPORTS
	#define XSCORE_API __declspec(dllimport)
	#ifdef _X64TARGET
		#pragma message("Statically linking XSCore90x64.lib in XSCore90.h")
		#pragma comment(lib, "XSCore90x64.lib")
	#else
		#pragma message("Statically linking XSCore90.lib in XSCore90.h")
		#pragma comment(lib, "XSCore90.lib")
	#endif
#endif

// 8 bits
//typedef uint8_t XBOOL;
typedef bool XBOOL;

enum XBOOL_VALUES
{
	xFALSE = false,
	xTRUE = true
};

// 64 bits
typedef uint64_t SENSORPID;

#ifndef NULL
#define NULL nullptr
#endif

enum EPressureUnit
{
	ePRESUNIT_MMHG = 0,	// millimeters of mercury
	ePRESUNIT_INH2O,	// inches of water
	ePRESUNIT_PSI,		// pounds/sq.inch
	ePRESUNIT_KPA,		// kilopascals
	ePRESUNIT_KGCM2,	// kgf/cm^2
	ePRESUNIT_ATM,		// atmospheres
	ePRESUNIT_NCM2,		// newtons/cm^2
	ePRESUNIT_MBAR,		// millibars
	ePRESUNIT_NM2,		// Newton/meter^2
	ePRESUNIT_GCM2,		// grams/cm^2
	ePRESUNIT_BAR,		// bar

	ePRESUNIT_RAW = 255
};

/* This Win32 structure is Copyright (c) Microsoft Corp. All rights reserved.
typedef struct _SYSTEMTIME {
	WORD wYear;
	WORD wMonth;
	WORD wDayOfWeek;
	WORD wDay;
	WORD wHour;
	WORD wMinute;
	WORD wSecond;
	WORD wMilliseconds;
} SYSTEMTIME, * PSYSTEMTIME, * LPSYSTEMTIME;
*/


// ===========================================================================
//	Configuration functions
// ===========================================================================

enum EXSErrorCodes
{
	eXS_ERRORCODE_OK,							// Function ran normally

	eXS_ERRORCODE_LIBRARY_NOT_INITIALIZED,		// The DLL library has not been initialized

	eXS_ERRORCODE_BADPARAMETER_OUTOFRANGE,		// a parameter is out of range
	eXS_ERRORCODE_BADPARAMETER_NULL,			// null parameter - pass in a variable/buffers address
	eXS_ERRORCODE_BADPARAMETER_INVALID_SENSOR_PID,	// either the PID is bad, or the sensor was not configured
	eXS_ERRORCODE_BADPARAMETER_BUFFERTOOSMALL,	// the buffer parameter is too small to hold the contents

	eXS_ERRORCODE_CREATEFOLDER_NOPERMISSION,	// the program doesn't have permission to create a folder at the specified location

	eXS_ERRORCODE_CALFILE_LOADFAILED,			// calibration file failed to load - likely the file wasn't found
	eXS_ERRORCODE_CALFILE_DOESNOTMATCHSENSOR,	// the calibration file does not match the sensor

	eXS_ERRORCODE_CONFIGURATION_NOTCOMPLETE,	// Call XS_ConfigComplete() to complete the sensor configuration.
	eXS_ERRORCODE_CONFIGURATION_NOSENSORS,		// no sensors have been added to the sample config via XS_AddSensorToConfig(), or could not be added
	eXS_ERRORCODE_CONFIGURATION_FAILCREATEXSN,	// Could not create the XSN file. Check that the path is valid and the location can be written too.
	eXS_ERRORCODE_AUTOCONFIG_SENSORNOTFOUND,	// no sensors found during enumeration - please check XS_GetLastEnumState()

	eXS_ERRORCODE_SENSORS_SENSORNOTFOUND,		// either the sensor isn't enumerated, or the PID is invalid
	eXS_ERRORCODE_SENSORS_RAWONLY,				// XS_GetPressure() called, but no calibration files have been loaded.  Only raw data is available.
	eXS_ERRORCODE_SENSORS_NOSAMPLE,				// XS_Sample() has not been called yet, or it has not succeeded in retrieving a sample

	eXS_ERRORCODE_SENSORS_CONNECTIONLOST,		// XS_Sample failed because a sensor was disconnected or USB power reset
	eXS_ERRORCODE_SENSORS_SAMPLETIMEOUT,		// XS_Sample failed because the sensor timed out while reading
	eXS_ERRORCODE_SENSORS_SAMPLEFAILED,			// XS_Sample failed for reasons unknown

	eXS_ERRORCODE_SENSORS_NOCONNECTION,			// Calling XS_Sample() without first calling to XS_OpenConnection()?
	eXS_ERRORCODE_SENSORS_CONNECTFAILED,		// It's possible that one of the sensors has become disconnected.  Check connections.
	eXS_ERRORCODE_SENSORS_COMMANDFAILED,		// The sensor did not respond properly to the command. Check connections or try the call again.

	eXS_ERRORCODE_MEMORYALLOCATION_FAILED,		// the system seems to be running low on memory, or the DLL could not allocate some memory
	eXS_ERRORCODE_COULDNOTCREATECAPTUREFILE,	// Could not create the target capture file

	eXS_ERRORCODE_SIMFILE_LOADFAIL,				// A problem occured while loading the simulation file.  The path might be incorrect, or the file cannot be opened.  (Try loading it in the XSENSOR desktop software.)
	eXS_ERRORCODE_SIM_FUNCTION_NA,				// The DLL function is not available or does nothing while in simulation mode.
	eXS_ERRORCODE_SIM_CALIBRATED_ONLY,			// The simulation only supports calibrated (pressure) data
	eXS_ERRORCODE_SIM_RAW_ONLY,					// The simulation only supports raw (non-pressure) data

	eXS_ERRORCODE_MANCAL_FUNCTION_NOTSET,		// The manaul calibration state is not set, which this function requires.
	eXS_ERRORCODE_MANCAL_FUNCTION_NA,			// The DLL function is not available or does nothing while in manual calibration mode.
	eXS_ERRORCODE_CALIBRATION_AUTOCACHE,		// This calibration function is disabled while the calibration auto-cache is enabled via XS_SetCalibrationFolder.

	eXS_ERRORCODE_X4CONFIGSCRIPT_COULDNOTOPEN,	// The X4 config script could not be opened. Perhaps a bad file path? Or the sensor is not an X4!
	eXS_ERRORCODE_X4CONFIGSCRIPT_BADRESPONSE,	// A command in the X4 config script returned a bad response

	eXS_ERRORCODE_X4SPKNOTCOMPATIBLEWITHCALFILE, // the selected X4 SPK is not compatible with the sensor's calibration file

	eXS_ERRORCODE_FAIL_X4REMOTE_ACTIVE,			// This local command failed because an X4REMOTE connection is active.
	eX4_ERRORCODE_FAIL_LOCAL_ACTIVE,			// This remote command failed because a session is open via XS_OpenConnection. X4 Remote connections are not compatible with this mode.
	eX4_ERRORCODE_DOWNLOAD_INTERRUPTED,			// The command was interrupted in the middle of downloading some state. Check connection and try again.
	eX4_ERRORCODE_UPLOAD_INTERRUPTED,			// The command was interrupted in the middle of uploading some state. Check connection and try again.

	eX4_ERRORCODE_SESSIONINDEX_OUTOFBOUNDS,		// the session file index is too large for the list.
	eX4_ERRORCODE_RECORDINGINPROGRESS,			// The command failed because the X4 is in the middle of a remote recording.
	eX4_ERRORCODE_REMOTENOTOPEN,				// the remote connection is not open. This command requires an open connection

	eX4_ERRORCODE_REMOTERECORD_STARTFAIL,		// the remote recording failed to start ... check connections
	eX4_ERRORCODE_REMOTERECORD_MISMATCHED,		// the sensors are mismatched (ie: two left feet) for a paired recording
	eX4_ERRORCODE_REMOTERECORD_NOT_INSOLE,		// A specified sensor is not an insole.
	eX4_ERRORCODE_REMOTERECORD_BADCMDRESPONSE,	// The command failed due to an unknown issue with the remote sensor. Try again!
	eX4_ERRORCODE_REMOTESAMPLE_CALNOTAVAILABLE, // there's no local calibration file and the X4 is busy recording (thus a cal file can't be downloaded)
};


// this is a bit mask - any number of these bits might be set
enum EEnumerationError
{
	eENUMERROR_OK						= 0x00000000,	// no errors detected

	eENUMERROR_NOSPKSDETECTED			= 0x00000001,	// no SPKS appear in the computer
	eENUMERROR_OPENDEVICEFAIL			= 0x00000002,	// The SPK could not be opened with CreateFile
	eENUMERROR_OPENDEVICEFAIL_PROCESSLOCK= 0x00000004,	// The SPK could not be opened because some other process has it opened
	eENUMERROR_HIDDEVICEENUMFAIL		= 0x00000008,	// The HID device enumerate failed - very low level

	eENUMERROR_MISSINGCON				= 0x00000010,	// The SPK is not connected to a sensor pad
	eENUMERROR_MISSINGDLLCODE			= 0x00000020,	// The sensor does not have a DLL code
	eENUMERROR_MISMATCHEDDLLCODE		= 0x00000040,	// The sensor's DLL code does not match this DLL
	eENUMERROR_MISSINGPROFILE			= 0x00000080,	// The sensors profile is not supported by this DLL

	eENUMERROR_MISSINGCHILDSPKS			= 0x00000100,	// This multi-SPK sensor is missing SPKS ports 2 to N
	eENUMERROR_MISSINGPARENTSPK			= 0x00000200,	// This multi-SPK sensor is missing SPK on port 1
	eENUMERROR_MISMATCHEEDFIRMWARE		= 0x00000400,	// This multi-SPK sensor must the same firmware on each SPK
	eENUMERROR_MISMATCHEDSPKTYPES		= 0x00000800,	// This multi-SPK sensor must the same SPK types on each port (either XS PRO, or just XS)

	eENUMERROR_CONNECTIONSENSE			= 0x00001000,	// This sensor pad is not properly plugged into the SPK - or there is a hardware problem with the sensor
	eENUMERROR_CONREQUIRESNEWERFIRMWARE	= 0x00002000,	// The sensor pad requires SPK(s) with firmware 1.3 or better
	eENUMERROR_MIXEDHSSX3				= 0x00004000,	// Mixed X3 and HSS components (either HSS sensor on X3, or X3 sensor on HSS)
	eENUMERROR_SENSORLOCK				= 0x00008000,	// The sensor is locked (likely due to time trial expiry)

	// the rest of the bits are reserved
};


// ===========================================================================
//	Library initialization/deinitialization
// ===========================================================================

extern "C" XSCORE_API EXSErrorCodes XS_GetLastErrorCode();
// Retrieves the last error code. Check this value when a function reports a failure. (See enum EXSErrorCodes)

extern "C" XSCORE_API const char* XS_GetLastErrorCodeAsString();
// Returns the last error codes in the form of an ASCII English string.

extern "C" XSCORE_API XBOOL XS_InitLibrary(XBOOL bThreadMode);
// Initialize the XS software engine. This must be the first call to the XS Library.
// When bThreadMode is xTRUE, the DLL samples independently of any calls to XS_Sample.
// When bThreadMode is xFALSE, the DLL waits for each XS_Sample call to fetch a new sample.
//
// Returns xTRUE if the call succeeded.

extern "C" XSCORE_API XBOOL XS_ExitLibrary();
// Uninitializes the XS software engine. Frees all allocated resources.  This should be the last call to the XS Library.

extern "C" XSCORE_API XBOOL XS_GetVersion(uint16_t& major, uint16_t& minor, uint16_t& build, uint16_t& revision);
// Fetch the DLL version - major.minor.build.revision.
//
// Returns xTRUE if the call succeeded.

// ===========================================================================
//	Sensor Enumeration
// ===========================================================================

extern "C" XSCORE_API uint32_t XS_EnumSensors();
// Scans the computer for all possible sensor connections and builds a list of connected sensors.
// 
// This function attempts to open a temporary connection to each candidate sensor. Some connections
// such as Bluetooth can take several seconds per candidate. The enumeration process can take
// between 5 and 180 seconds, depending on what type of sensors have been selected for enumeration
// and the general state of the computer.
// 
// Any sensors connected to a computer after an initial XS_EnumSensors call will not be seen
// until a subsequent call to XS_EnumSensors is made.
//
// Returns the number for found sensors.

extern "C" XSCORE_API void XS_SetAllowEnumInterruptX4Remote(XBOOL allow);
extern "C" XSCORE_API XBOOL XS_GetAllowEnumInterruptX4Remote();
// XS_EnumSensors normally interrupts remote recording sessions for X4 sensors.
// This is required to query the X4 sensor for its information. Remote session recordings
// prevent this information from being retrieved.
// 
// Set this to xFALSE to prevent XS_EnumSensors from interrupting any active remote recordings.

extern "C" XSCORE_API void XS_SetAllowFastEnum(XBOOL bAllow);
extern "C" XSCORE_API XBOOL XS_GetAllowFastEnum();
// When this flag is enabled, the DLL skips looking for new sensors and only attempts to talk 
// to sensors it already knows about. Temporarily enable this flag this when scanning for a known sensor
// whose connection was lost. This avoids the expense of looking for new sensors.


extern "C" XSCORE_API EEnumerationError XS_GetLastEnumState();
// Retrieves an error bit mask indicating why XS_EnumSensors or XS_AutoConfig* returned 0.
// One or more errors may have occurred and are OR'd into a bitmask. See enum EEnumerationError for details.

extern "C" XSCORE_API const char* XS_GetLastEnumStateAsString();
// Retrieves an internal English string describing the errors.

extern "C" XSCORE_API uint32_t XS_EnumSensorCount();
// Returns a count of the number of sensors found during the XS_EnumSensors() call.

extern "C" XSCORE_API SENSORPID XS_EnumSensorPID(uint32_t nEnumIndex);
// Returns a sensor's 64-bit product ID at the indexed (0-index) location of the enumerated sensors list.
// If the return value is 0, the function call failed. Failure is typically caused by an index that is out of bounds.


// ===========================================================================
//	Sensor Details
// ===========================================================================

extern "C" XSCORE_API uint16_t XS_GetSerialFromPID(SENSORPID spid);
// Returns a sensor's 4 digit serial number (ie: 0014)

extern "C" XSCORE_API XBOOL XS_GetSensorDimensions(SENSORPID spid, uint16_t& nRows, uint16_t& nColumns);
// Fetch the number of rows and columns defining the sensor grid.
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_GetSensorName(SENSORPID spid, uint32_t& charCount, wchar_t* pBuffer = NULL);
extern "C" XSCORE_API XBOOL XS_GetSensorNameUTF8(SENSORPID spid, uint32_t& charCount, char* pBuffer = NULL);
// Fetch the display name of the sensor. Example: HX210.11.31.M9-LF S0002
//
// The string is made of 16 bit wchar_t characters (UTF-16/UCS-2) which is null terminated.
//
// If pBuffer is 0, the length of the required buffer (in wchar_t character
// counts) is returned in bufferSize. This count includes space for a null terminator
// character.  (Byte size of the buffer should be at least 2 x charCount).
//
// If pBuffer is valid, then charCount is expected to be the number of wchar_t
// that pBuffer can hold (including the zero terminator).
// Returns xTRUE if the call succeeds.


extern "C" XSCORE_API XBOOL XS_GetSenselDims(SENSORPID spid, float& nWidthCM, float& nHeightCM);
// Fetch the physical dimensions of a single cell in centimeters. 
// This function is only usable after a sensor configuration is created.
// Returns xTRUE if the dimensions could be fetched.

extern "C" XSCORE_API XBOOL XS_IsX4Sensor(SENSORPID spid);
// Returns xTRUE if this an X4 sensor.

extern "C" XSCORE_API XBOOL XS_IsX4FootSensor(SENSORPID spid, XBOOL& bFootSensor, XBOOL& bLeftFoot);
// Returns xTRUE if this an X4 sensor.
// Sets bFootSensor to xTRUE if the sensor is an X4 foot sensor. 
// Sets bLeftFoot to xTRUE if it's a left foot sensor, and xFALSE for right foot sensors.


// ===========================================================================
//	Calibration Management
// ===========================================================================

extern "C" XSCORE_API XBOOL XS_SetCalibrationFolder(const wchar_t* szCalibrationFolder);
extern "C" XSCORE_API XBOOL XS_SetCalibrationFolderUTF8(const char* szCalibrationFolder);
// When the DLL is provided with a folder for caching calibration files, it will automatically
// manage downloading and selection of an appropriate calibration file.
// While enabled, the other calibration file functions are not enabled.
//
// Typically, this is the best option for managing calibration files
//
// Alternatively, the following functions for direct management of a sensor's calibration files:
// XS_DownloadCalibrations; XS_GetCalibrationName; XS_GetCalibrationInfo; XS_GetCalibrationInfoEx
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API uint32_t XS_DownloadCalibrations(SENSORPID spid, const wchar_t* szCalibrationFolder);
extern "C" XSCORE_API uint32_t XS_DownloadCalibrationsUTF8(SENSORPID spid, const char* szCalibrationFolder);
// Downloads the calibration files stored on the sensor and saves them to a folder.
// Returns number of files downloaded. There may be 0, 1 or more calibration files on the sensor.  
// If 0 is returned, call XS_GetLastErrorCode to determine if an error occurred.
// Usually When more than one file is present, each file is a different calibrated pressure range.


extern "C" XSCORE_API XBOOL XS_GetCalibrationName(uint32_t nCalIndex, uint32_t& dwBufferSize, wchar_t* pBuffer = NULL);
extern "C" XSCORE_API XBOOL XS_GetCalibrationNameUTF8(uint32_t nCalIndex, uint32_t & dwBufferSize, char* pBuffer = NULL);
// This function retrieves the full file path and file name of the indexed
// calibration file. The index is 0-based.
// This function only works after a calling XS_DownloadCalibrations, and that
// function returns a count of 1 or more.
//
// If pBuffer is NULL, the size of the required buffer (in bytes) is returned
// in dwBufferSize. This includes space for a null terminator.
// 
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_GetCalibrationInfo(const wchar_t* szCalibrationFile, uint8_t pressureUnits, float& nMinPressure, float& nMaxPressure);
extern "C" XSCORE_API XBOOL XS_GetCalibrationInfoUTF8(const char* szCalibrationFile, uint8_t pressureUnits, float& nMinPressure, float& nMaxPressure);
// Scans the calibration file and returns its pressure range (using the pressure units - see enum EPressureUnit)
//
// szCalibrationFile is the full path to the file on disk.  eg: c:\\CalFiles\\MyCalFile.xsc
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_GetCalibrationInfoEx(const wchar_t* szCalibrationFile, SENSORPID & spid);
extern "C" XSCORE_API XBOOL XS_GetCalibrationInfoExUTF8(const char* szCalibrationFile, SENSORPID & spid);
// Retrieves the SENSORPID associated with the calibration file.
// szCalibrationFile is the full path to the cal file on disk.  eg: c:\\CalFiles\\MyCalFile.xsc
// Returns xTRUE if the call succeeds.


// ===========================================================================
//	Sensor Configuration - AUTOMATIC
//
//	These functions simplify the process of configuring any connected sensors.
// ===========================================================================

extern "C" XSCORE_API XBOOL XS_AutoConfigByDefault();
extern "C" XSCORE_API XBOOL XS_AutoConfigByDefaultXSN(const wchar_t* szXSNFile);
extern "C" XSCORE_API XBOOL XS_AutoConfigByDefaultXSNUTF8(const char* szXSNFile);
// Constructions a sensor configuration using all found sensors. Default
// calibration pressure ranges are utilized.
// This function sets the pressure units to ePRESUNIT_MMHG! Be sure to call
// XS_SetPressureUnit() after calling this function.
// 
// The XSN variant function takes a full file path and filename to construct
// an XSENSOR session file from all recorded frames.
//
// Example:  
//  wchar_t* szPath[] = L"c:\\mysessions\\session5.xsn";
//	XS_AutoConfigByDefaultXSN(szPath);
//  
// *OR*
//  char_t* szPath[] = "c:\\mysessions\\session5.xsn";
//	XS_AutoConfigByDefaultXSNUTF8(szPath);
//
// Returns xTRUE if the call succeeds.


extern "C" XSCORE_API XBOOL XS_AutoConfig(uint8_t pressureUnits = ePRESUNIT_MMHG, float targetPressure = -1.0f);
// Constructions a sensor configuration using all found sensors. 
// If targetPressure is -1.0, then the default calibration pressure range is used.
// If targetPressure is >= 0, then the nearest matching pressure range is used.
// Sets the calibrated data's pressure units (see enum EPressureUnits).
// Pressure readings are presented in these units. 
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_AutoConfigXSN(const wchar_t* szXSNFile, uint8_t pressureUnits = ePRESUNIT_MMHG, float targetPressure = -1.0f);
extern "C" XSCORE_API XBOOL XS_AutoConfigXSNUTF8(const char* szXSNFile, uint8_t pressureUnits = ePRESUNIT_MMHG, float targetPressure = -1.0f);
// The XSN variant of XS_AutoConfig function takes a full file path and filename
// and constructs an XSENSOR session file from all recorded frames.
// See XS_AutoConfigByDefaultXSN for file path example.
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_AutoConfig_SingleSensor(const wchar_t* szCalFile = NULL);
extern "C" XSCORE_API XBOOL XS_AutoConfig_SingleSensorUTF8(const char* szCalFile = NULL);
extern "C" XSCORE_API XBOOL XS_AutoConfig_SingleSensorXSN(const wchar_t* szXSNFile, const wchar_t* szCalFile = NULL);
extern "C" XSCORE_API XBOOL XS_AutoConfig_SingleSensorXSNUTF8(const char* szXSNFile, const char* szCalFile = NULL);
// These XS_AutoConfig variants allow manual selection of the calibration file. 
// This only works if there is a single sensor present.


// ===========================================================================
//	Sensor Configuration - MANUAL
//
//	These functions give better control over the configuration of any connected
//	sensors.
// ===========================================================================

extern "C" XSCORE_API XBOOL XS_NewSensorConfig();
// Prepares the library for creating a configuration of sensors.
// Remove any existing sensor configuration.
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_NewSensorConfigXSN(const wchar_t* szXSNFile);
extern "C" XSCORE_API XBOOL XS_NewSensorConfigXSNUTF8(const char* szXSNFile);
// Similar to XS_NewSensorConfig(), but also creates a standalone XSN session file.
// The szXSNFile file path must be fully specified. eg: "c:\MySessions\Test.xsn".
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_AddSensorToConfig(SENSORPID spid, const wchar_t* szCalibrationFile);
extern "C" XSCORE_API XBOOL XS_AddSensorToConfigUTF8(SENSORPID spid, const char* szCalibrationFile);
// Adds a sensor to the sensor configuration.
// The full path to the sensor's calibration file should be specified in szCalibrationFile.
// If szCalibrationFile is 0, then only raw data is collected.
//
// Returns xTRUE if the call succeeds.
//
// NOTE: All sensors in the configuration must have calibration files,
//       otherwise only raw values are collected.

extern "C" XSCORE_API XBOOL XS_AddSensorToConfig_AutoCal(SENSORPID spid, uint8_t pressureUnits = ePRESUNIT_MMHG, float nTargetMaxPressure = -1.0f);
// Adds a sensor to the sensor configuration. Will download any calibration
// files from the sensor if they are not present.
// Attempts to use the nearest matching calibration pressure range.
// Returns xTRUE if the call succeeds.
//
// NOTE: The calibration download process can be slow. Be sure to set a folder 
//       for caching the calibration files using XS_SetCalibrationFolder().

extern "C" XSCORE_API XBOOL XS_AddSensorToConfig_AutoCalByDefault(SENSORPID spid);
// Similar to XS_AddSensorToConfig_AutoCal(), but attempts to use the default
// pressure range for the sensor.
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_ConfigComplete();
// When finished adding sensors to the configuration, call this function
// to initialize the configuration for use.
// This function must be called before calling XS_OpenConnection.
// Returns xTRUE if the call succeeds.

// ===========================================================================
// ===========================================================================
//	Sensor Configuration
// ===========================================================================
// ===========================================================================

extern "C" XSCORE_API void XS_SetPressureUnit(uint8_t PressureUnit);
// Sets the calibrated data's pressure units (see enum EPressureUnits).
// Pressure readings are presented in these units. 
// These can be changed at any time.

extern "C" XSCORE_API uint8_t XS_GetPressureUnit();
// Returns the current pressure units (see enum EPressureUnits).

extern "C" XSCORE_API XBOOL XS_HasConfig();
// Returns xTRUE if the DLL has a sensor configuration.

extern "C" XSCORE_API XBOOL XS_ReleaseConfig();
// Closes any open connection and releases the configuration (including any XSN file).
// Subsequent calls to XS_OpenConnection will fail until a new config is created.
// Call this before attempting any 

// ===========================================================================
//	Sensor Configuration - details
// ===========================================================================

extern "C" XSCORE_API SENSORPID XS_ConfigSensorPID(uint32_t nConfigIndex);
// Returns the sensor PRODUCT ID at the indexed location of the configured
// sensors list. The index is zero based.
// If 0 is returned, check XS_GetLastErrorCode.

extern "C" XSCORE_API uint32_t XS_ConfigSensorCount();
// Returns the number of configured sensors.

extern "C" XSCORE_API XBOOL XS_IsCalibrationConfigured();
// Returns xTRUE if the configuration is setup for calibrated data.

extern "C" XSCORE_API XBOOL XS_GetConfigInfo(uint8_t pressureUnits, float& nMinPressure, float& nMaxPressure);
// After configuration is complete, call this to check the pressure range of the configuration.
// 
// pressureUnits - the returned minimum and maximum pressures are returned
//                 in these units. (See enum EPressureUnits).
// 
// When operating in RAW mode (i.e.: no calibration file specified), pressureUnits is ignored.
// Returns xTRUE if the call succeeds.


// ===========================================================================
//	Sampling State
//
// These functions affect the sampling behavior of the DLL.
// These settings should only be modified before opening a connection.
// ===========================================================================

extern "C" XSCORE_API void XS_SetReadTimeout(uint32_t TimeoutSeconds);
// Sets the XS_Sample function's timeout period in seconds.
//
// If the software loses connection to a sensor, it tries to re-open the connection
// for this length of time.

extern "C" XSCORE_API uint32_t XS_GetReadTimeout();
// Returns the XS_Sample timeout period in seconds.


extern "C" XSCORE_API void XS_SetOverlapMode(XBOOL bOverlap);
// This mode causes the DLL to sample each configured sensor in sequence (versus in parallel).
//
// This mode prevents electrical crosstalk between sensors when they
// are physically in contact.
// 
// NOTE: This mode is not available when X4 sensors are configured.

extern "C" XSCORE_API XBOOL XS_GetOverlapMode();
// returns xTRUE when Overlap mode is on.  Overlap mode is off by default.

extern "C" XSCORE_API void XS_SetAllowWireless(XBOOL bAllow);
extern "C" XSCORE_API XBOOL XS_GetAllowWireless();
// A flag that allows use of the X3 wireless series.

extern "C" XSCORE_API void XS_SetAllowX4(XBOOL bAllow);
extern "C" XSCORE_API XBOOL XS_GetAllowX4();
// A flag that allows use of the X4 sensor series (wired).

extern "C" XSCORE_API void XS_SetAllowX4Wireless(XBOOL bAllow);
extern "C" XSCORE_API XBOOL XS_GetAllowX4Wireless();
// A flag that allows use of the X4 sensor series (wireless - must already be paired in the OS).

// NOTE: There is no flag for X3 wired sensors. These are always enumerated.


extern "C" XSCORE_API void XS_SetX4Mode8Bit(XBOOL bEnable8BitMode);
extern "C" XSCORE_API XBOOL XS_GetX4Mode8Bit();
// A flag that puts the X4 in 8-bit mode.
// - This can improve the reliability of Bluetooth transmission speeds. It has no
//   impact on actual recording speed.

extern "C" XSCORE_API XBOOL XS_HasHardwareIMU(SENSORPID spid);
// determines if the sensor has IMU capability

extern "C" XSCORE_API void XS_SetEnableIMU(XBOOL bEnable);
// Enables/disables IMU collection for supported sensors.

extern "C" XSCORE_API XBOOL XS_GetEnableIMU();
// Indicates whether the IMU enable flag is set. (Does not indicate whether IMU is supported!)


extern "C" XSCORE_API void XS_SetStreamingMode(XBOOL bStreaming, uint16_t streamingMaxFrameCache);
// Streaming mode buffers all incoming frames and releases them with each XS_Sample() call.
// When streaming mode is off, sensors are sampled at the time XS_Sample is called.
//
// NOTE: When streaming mode is on, the DLL will allocate large amounts of buffer
// memory if the samples are not consumed fast enough.
//
// The streamingMaxFrameCache parameter determines how many frames the streaming mode buffers. 
// This is the cache limit.
// If streamingMaxFrameCache is set to zero, then the DLL caches all frames until it runs out of memory.
// If streamingMaxFrameCache is non-zero, the DLL discards older frames once the cache limit is reached.

extern "C" XSCORE_API XBOOL XS_GetStreamingMode();
// Returns xTRUE if streaming mode is on, xFALSE otherwise.  This is off by default.


extern "C" XSCORE_API void XS_SetSampleAverageCount(uint16_t nCount);
// Set the number of per-sensel readings that are averaged together per sensel scan.
// 
// This averaging occurs within the sensor's DSP hardware. Higher cycles lead to slower
// frame rates but may result in a better signal-to-noise ratio.
//
// Valid X3 numbers are 1, 2, 4, 8 and 16.
// X4 sensors can only run at 4 and 8 cycles. X4 foot sensors run fastest with 4 cycles.
//
// This value can only be set before calling any of the XS_AutoConfig* functions or XS_ConfigComplete().
// Typically, this value does not need to be set as the sensor is normally programmed with an expected default.

extern "C" XSCORE_API uint16_t XS_GetSampleAverageCount();
// Get the number of per-sensel readings that are averaged together per sensel scan.


// ===========================================================================
//	Connection Management
// ===========================================================================

extern "C" XSCORE_API XBOOL XS_OpenConnection(uint32_t nThreadedFramesPerMinute=0);
// Opens all configured sensors and begins sampling.
//
// Call this only after calling XS_ConfigComplete() or XS_AutoConfig*().
//
// nThreadedFramesPerMinute
//	- When using the DLL in threaded mode (ie: XS_InitLibrary(xTRUE)),
//    this specifies the target framerate in frames per minute. eg: 600 FPM = 10 Hz
//
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_IsConnectionOpen();
// returns xTRUE if the connection is open.
//
// Typically, this function returns xFALSE when a sensor is disconnected, or
// a sensor is in use by another program.

extern "C" XSCORE_API XBOOL XS_CloseConnection();
// Stops all sampling and closes the sensor connections.
//
// If the sensor configuration is using an XSN file, then that file stays open. 
// Subsequent calls to XS_OpenConnection continue to write to the same XSN file.
//
// To close the XSN file, call XS_ReleaseConfig.


extern "C" XSCORE_API XBOOL XS_IsConnectionThreaded();
// Returns xTRUE if the connection is open and the connection is running in an asynchronous threaded mode.


// ===========================================================================
//	Sampling
// ===========================================================================

extern "C" XSCORE_API XBOOL XS_SetNoiseThreshold(float threshold);
// Any pressure readings below this noise threshold are zeroed. The threshold is applied
// to all configured sensors.
//
// The default threshold is normally the lowest calibrated pressure of all configured sensors.
//
// threshold - The threshold should be in the active pressure units. (see XS_GetPressureUnit)

extern "C" XSCORE_API float XS_GetNoiseThreshold();
// Returns the threshold below which pressure is zeroed.
// If -1.0 is returned, this indicates the function failed. Check XS_GetLastErrorCode.

extern "C" XSCORE_API XBOOL XS_Sample();
// Ask the configured sensors to record a new sample to an internal buffer.
// Use XS_GetPressure() to retrieve the pressure map from the internal buffer.
//
// When using the library in a threaded mode, this call returns immediately. 
// However, the internal buffer may or may not have a new sample as it only updates
// when a new one is available. Check the timestamp to see if it has changed.
//
// When using the library in an un-threaded mode, this call blocks until a
// sample is recorded or a read timeout occurs.
// 
// Returns xTRUE if the call succeeds. Note this does not necessarily mean there is
// a new sample ready. Be sure to check timestamps!

extern "C" XSCORE_API XBOOL XS_GetSampleTimestampUTC(
	uint16_t& year, uint8_t& month, uint8_t& day, 
	uint8_t& hour, uint8_t& minute, uint8_t& second, uint16_t& millisecond);
// Fetch the timestamp of the last sample collected.
// Components are normal UTC ranges. month (1-12), day (1-31). Hour is (0-23),
// minute and second (0-59), millisecond (0-999)

extern "C" XSCORE_API XBOOL XS_GetSampleTimeUTC(SYSTEMTIME & tTime);
// Fetch the timestamp of the last sample collected.
// Similar to XS_GetSampleTimestampUTC, but using the Win32 structure SYSTEMTIME.

extern "C" XSCORE_API XBOOL XS_GetSampleTimestampExUTC(
	uint16_t& year, uint8_t& month, uint8_t& day, 
	uint8_t& hour, uint8_t& minute, uint8_t& second, 
	uint16_t& millisecond, uint16_t& microsecond, bool bAsLocalTime);
// Fetch the timestamp of the last sample collected.
// Includes microseconds when supported by the sensor hardware.
// This version allows conversion of the timestamp to the local time zone.


extern "C" XSCORE_API XBOOL XS_GetPressure(SENSORPID spid, float* pData);
// Retrieves the calibrated sample data for a single sensor. 
//
// (Call XS_Sample once for all sensors before calling XS_GetPressure for each sensor.)
//
// The pressure readings are in the units set by XS_SetPressureUnit() or XS_AutoConfig().
//
// pData 
//	- pass in a pre-allocated buffer which is larger enough to hold (rows X columns)
//    elements, each 32-bits.
//	- rows and columns are the dimensions of the sensor.
//	- The array is organized in a typical row-major order. IE: The first N values
//    in the array correspond 
//		to the first row, where N is the number of columns.
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_GetPressureSafe(SENSORPID spid, uint32_t dataCount, float data[]);
// This version takes a preallocated buffer of floats (32-bit).
// dataCount is the number of elements in the data[] array.
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_GetRaw(SENSORPID spid, uint16_t* pData);
// Similar to XS_GetPressure(), except it takes an array of uint16_t and returns
// uncalibrated raw 16 bit values from the sensor.
// Returns xTRUE if the call succeeds.


extern "C" XSCORE_API XBOOL XS_GetRawSafe(SENSORPID spid, uint32_t dataCount, uint16_t data[]);
// This version takes a preallocated buffer of uint16_t (16-bit).
// dataCount is the number of elements in the data[] array.
// Returns xTRUE if the call succeeds.

extern "C" XSCORE_API XBOOL XS_GetIMU(
	SENSORPID spid,
	float& qx, float& qy, float& qz, float& qw,
	float& ax, float& ay, float& az,
	float& gx, float& gy, float& gz);
// Fetches the IMU data (if any) for the current Sample

extern "C" XSCORE_API XBOOL XS_GetHardwareFrameState(
	SENSORPID spid,
	uint32_t& sequence, uint32_t& ticks);
// Retrieves the hardware frame header state. 'sequence' increments for 
// each frame. 'ticks' is milliseconds.
// Returns xFALSE if there is no hardware state, or an error has occurred

extern "C" XSCORE_API float* XS_AllocPressureBuffer(SENSORPID spid);
// Allocate a buffer for accessing the pressure values. Use this for multiple readings.
// The DLL will allocate enough memory to hold all rows and columns of the sensor.
// Returns 0 if the SENSORPID is invalid or the system is low in memory.

extern "C" XSCORE_API void XS_ReleasePressureBuffer(float* pBuffer);
// Releases the DLL allocated buffer.

extern "C" XSCORE_API uint16_t * XS_AllocRawBuffer(SENSORPID spid);
// Allocate a buffer for accessing the raw values. Use this for multiple readings.
// The DLL will allocate enough memory to hold all rows and columns of the sensor.
// Returns 0 if the SENSORPID is invalid or the system is low in memory.

extern "C" XSCORE_API void XS_ReleaseRawBuffer(uint16_t * pBuffer);
// Releases the DLL allocated buffer.


XSCORE_API XBOOL XS_GetDeadMap(SENSORPID spid, uint8_t* pData);
// Maps out the sensels that are dead and alive.  1 = dead, 0 = alive
// Only profiles that mask out dead cells in the grid will have this. (ie: X4 foot sensors)
// "uint8_t* pData" should be allocated with space for ROWS x COLUMNS for the target sensor


// ===========================================================================
//	Frame Statistics
// ===========================================================================

extern "C" XSCORE_API XBOOL XS_CenterOfPressure(SENSORPID spid, float zeroThreshold, float& column, float& row);
// Computes the center of pressure (COP) of the last sample recorded.
//
// The coordinates have negative values if there is a problem. Call XS_GetLastErrorCode() if that occurs.
//
// The center of pressure calculation ignores pressure which is below the zero threshold.
// zeroThreshold must be in the same pressure units as XS_GetPressureUnits().
//
// Row coordinates are from 1 to row count.
// Column coordinates are from 1 to column count.
// 
// Row and column counts are retrieved with XS_GetSensorDimensions().
//
// Whole numbers (no fractions) indicate the COP is over the center of the sensel.
//
// The fractional part of the coordinate indicates a normalized distance between
// the centers of two sensels.
//
// Example
// Suppose the function returns these values: column = 1.53f; row = 2.25f.
// This means the COP is 53% of the distance between the center of column 1 and
// the center of column 2. The COP is 25% of the distance between the center
// of row 2 and the center of row 3. (It is closer to row 2).


// ===========================================================================
// UTILITY FUNCTIONS
// ===========================================================================

extern "C" XSCORE_API XBOOL XS_WideToUTF8(const wchar_t* wide, uint32_t & bufferSize, char* utf8);
// Converts a wide string (wchar_t) to UTF8. You must supply a UTF8 buffer that is
// large enough to hold the converted string.
// The string is expected to be null (zero) terminated.
//
// const wchar_t* wide
//  - the wide string to convert
// 
// uint32_t& bufferSize 
//	- returns the size of the buffer (in byte count) needed to hold the conversion. 
//  - If utf8 is not null, pass in the utf8's buffer size in this field to allow 
//    for an extra buffer safety check.
// 
// char* utf8 
//	- the buffer to hold the utf8 string. Pass in nullptr (or 0) to retrieve just
//    the size of the buffer (in bytes) required in bufferSize.

extern "C" XSCORE_API XBOOL XS_UTF8ToWide(const char* utf8, uint32_t & bufferSize, wchar_t* wide);
// Converts a UTF8 (or plain ASCII) string to wide format (wchar_t). You must supply a wchar_t* buffer that is large enough to hold the converted string.
// The string is expected to be null (zero) terminated.
//
// const char* utf8
//  - the utf8/ASCII string to convert
// 
// uint32_t& bufferSize 
//	- returns the size of the buffer (in byte count) needed to hold the conversion. 
//    wchar_t uses 2 bytes per character.
//  -  (eg: If bufferSize == 100, then  wchar_t wide[50]  will hold the string.
//  - If wide is not null, pass in the wide's buffer size (in bytes) in this field
//    to allow for an extra buffer safety check.
// 
// wchar_t* wide 
//	- the buffer to hold the wide string. Pass in nullptr (or 0) to retrieve just 
//    the size of the buffer (in bytes) required in bufferSize.



// ===========================================================================
//	X3 PRO HUB - External Sync - X3 sensors only
// ===========================================================================

// Enables the external sync trigger.  Once enabled, the XS_Sample() function will
// block until the X3 PRO hub receives a signal, or the read-timeout timer expires.
//
// The hub allows two types of synchronization: "trigger start of streaming" and 
// "trigger single frame".
// 
// There are two types of triggers and only one may be enabled at a time
// 
// Enabling
// one trigger automatically disables the other trigger.


// NOTE: Be sure to set a ReadTimeout period that is larger than your expected trigger
//       frequency.
//

// For reference, here are the operational specs for the external sync port:
//
// The sync connector is a 3.5mm stereo jack.  Position 1 is GND, position 2 is the sync voltage.
// The voltage is LV TTL (0 to 3.6V max).  Higher voltages are possible by using
// an external series resistor in line with the sync voltage.
//
// The following equation can be used to calculate the series resistor value:
// 
// Rseries = Vsync*75 - 264

extern "C" XSCORE_API XBOOL XS_IsRecordTrigger_FirstFrameOnly();
// Returns xTRUE if this trigger is enabled.

extern "C" XSCORE_API void XS_EnableRecordTrigger_FirstFrameOnly(XBOOL bEnable);
// The "FirstFrameOnly" trigger blocks the XS_Sample() command until the XS PRO
// hub is signaled on the external sync port.  Subsequent calls to XS_Sample()
// return immediately with a collected sample.

extern "C" XSCORE_API XBOOL XS_IsRecordTrigger_EachFrame();
// Returns xTRUE if this trigger is enabled.

extern "C" XSCORE_API void XS_EnableRecordTrigger_EachFrame(XBOOL bEnable);
// The "EachFrame" trigger blocks the XS_Sample() command until the XS PRO
// hub is signaled on the external sync port.  Subsequent calls to XS_Sample()
// also block until the port is signaled.



// ===========================================================================
//	X4 Remote Connection Management
// 
//  These functions allow starting & stopping remote X4 recordings (made to
//  the onboard SD card), as well as managing the files.
// 
//  These functions should not be used in the context of live sessions created
//  with XS_OpenConnection().
// 
//  The function calls in this block should be made in the context of an open 
//  remote connection.
// ===========================================================================

extern "C" XSCORE_API XBOOL X4_OpenRemote(SENSORPID spid);
// Opens a remote connection to an X4 sensor. Can fail if the sensor doesn't not have 
// an SD card, check error codes.
// The initial open call may take a while as the DLL downloads (and caches) various 
// sensor details on the first call.

extern "C" XSCORE_API XBOOL X4_CloseRemote(SENSORPID spid);
// Closes a remote connection to an X4 sensor.

extern "C" XSCORE_API XBOOL X4_IsRemoteRecording(SENSORPID spid, XBOOL* remoteRecording);
// Is the X4 currently recording remotely?
// Sets remoteRecording to xTRUE if it is.

extern "C" XSCORE_API XBOOL X4_StartRemoteRecording(SENSORPID spid, float framesPerSecond);
// Starts the X4's remote recording.

extern "C" XSCORE_API XBOOL X4_StopRemoteRecording(SENSORPID spid);
// Stops the X4's remote recording. This ends the active session.

extern "C" XSCORE_API XBOOL X4_StartRemotePairRecording(SENSORPID spid_left_insole, SENSORPID spid_right_insole, float framesPerSecond);
// Starts a synchronized recording for two X4 foot sensors (left and right insoles only)

extern "C" XSCORE_API XBOOL X4_StopRemotePairRecording(SENSORPID spid_left_insole, SENSORPID spid_right_insole);
// Stops a synchronized recording

extern "C" XSCORE_API XBOOL X4_SampleRemote(SENSORPID spid);
// Fetches a preview frame from the sensor. Call XS_GetPressure() to get the frame.
// Only available when a calibration file is cached.
// Be careful to limit the calls to this as it may interfer with the remote recording.

extern "C" XSCORE_API XBOOL X4_GetRemoteSampleRange(SENSORPID spid, uint8_t pressureUnits, float* minPressure, float* maxPressure);
// Fetch the pressure range of the remote sample.
// Only valid after at least one successful call to X4_SampleRemote()

extern "C" XSCORE_API XBOOL X4_GetRemoteDuration(SENSORPID spid, float framesPerSecond, uint32_t* minutes);
// For a given recording speed, returns the available duration of recording in total minutes.
// This is based on SD card space and not battery life.
// This information is not available when a recording is running.

// ===========================================================================
// X4 REMOTE SESSION COMMANDS
// ===========================================================================

#if(0) // work in progress - 2022-Sep-26 - T.RUSSELL - XSENSOR TECH.
extern "C" XSCORE_API XBOOL X4_FetchRemoteSessionList(SENSORPID spid, uint32_t & sessionCount);
// Retrieves the list of sessions currently on the remote sensor. The list is held internally by the DLL. Check sessionCount for a non-zero value.

extern "C" XSCORE_API XBOOL X4_AccessRemoteSessionInfo(
	SENSORPID spid, uint32_t sessionIndex, 
	uint32_t & fileSize, 
	bool& isPairedSession, 
	uint32_t & nameBufferSize, 
	char* sessionName);
// Accesses the retrieved internal session list via a 0-based session index.
//
// uint32_t& fileSize
//  - indicates the size of the session file in bytes
//
// bool& isPairedSession
//	- indicates if the session is expected to be paired with another sensor's remote session. -XTK#### indicates the common pairing token between the two sessions.
//
// uint32_t& nameBufferSize
//  - returns the expected buffer size (in bytes) to hold the session name. Pass in the known buffer size of the name buffer for extra safety.
//
// char* sessionName
//	- the buffer to hold the session name (utf8/ascii).
//  - pass in nullptr (or 0) to just retrieve the size of the required buffer in nameBufferSize
//  - when passing in the buffer, set nameBufferSize to the size of the buffer for an extra buffer safety check


extern "C" XSCORE_API XBOOL X4_DownloadRemoteSession(
	SENSORPID spid, 
	const char* sessionName, 
	const char* sessionFolder, 
	bool bDeleteRemoteOnSuccess, 
	uint8_t * progressPct);
// Downloads the named session to the target folder. The DLL will attempt to create the folder if it doesn't exist.
// NOTE: The operation must be done within the context of a fetched session list!
// 
// const char* sessionName
//  - the session name as found in the session list
// 
// const char* sessionFolder
//  - a folder on the PC. The string is in UTF8 format. If you have a wchar_t string, use XS_WideToUTF8 to convert it.
// 
// bool bDeleteRemoteOnSuccess
//  - set true to delete the remote session file if the download succeeds.
// 
// uint8_t* progressPct
//  - (optional) an integer percentage of download completion. On error or issue, the value is set to 255.
//
// The downloaded session is in the original .x4r format. Use X4_ConvertSession or X4_ConvertSessionPair to generate an XSN file.
//
// This function may take a while and may be run on its own thread, however don't call any other DLL functions while running the threaded function.
//
// NOTE: See X4_ConvertSession() comments for an example of threaded use.


extern "C" XSCORE_API XBOOL X4_DeleteRemoteSession(SENSORPID spid, const char* session);
// Deletes the named remote session from the SD card.
// NOTE: The operation must be done within the context of a fetched session list!


extern "C" XSCORE_API XBOOL X4_ConvertSession(const char* sessionX4R, const char* folderXSN, uint8_t * progressPct);
// Converts an X4R session file into a XSN session.
//
// const char* sessionX4R
//	- full path and file name of the X4R session file.
//
// const char* folderXSN
//  - the folder where the XSN file will be constructed. The DLL will attempt to create the folder if it doesn't exist.
//  - the constructed XSN file has the same name as the X4R file with a different file extension.
// 
// uint8_t* progressPct
//  - (optional) an integer percentage of download completion. On error or issue, the value is set to 255.
//
// This function may take a while and may be run on its own thread. However, don't call any other DLL functions while running the threaded function.
// 
// Example Win32 Threaded Usage:
/*
	struct ConvertSession
	{
		ConvertSession()
		{
			sessionX4R = nullptr;
			folderXSN = nullptr;
			progressPct = 0;
			eLastError = EXSErrorCodes::eXS_ERRORCODE_OK;
			result = xFALSE;
			bRunning = false;
		}

		const char* sessionX4R;
		const char* folderXSN;
		uint8_t progressPct;
		EXSErrorCodes eLastError;
		XBOOL result;
		bool bRunning;
	};

	UINT __stdcall THREAD_ConvertSession(LPVOID lpParam)
	{
		ConvertSession* session = (ConvertSession*)lpParam;

		session->bRunning = true;
		session->result = X4_ConvertSession(session->sessionX4R, session->folderXSN, &(session->progressPct));
		
		session->eLastError = XS_GetLastErrorCode();
		session->bRunning = false;

		return 1;
	}

	#include <thread>
	#include <assert.h>

	void MyFunc()
	{
		ConvertSession session;
		session.sessionX4R = "c:\\mysessions\\x20210621-175348927-HX2101131M9RF-S0013.x4r";
		session.folderXSN = "c:\\mysessions\\processedXSN";
		session.bRunning = true;

		std::thread myThread = std::thread(THREAD_ConvertSession, &session);

		if (myThread.joinable())
		{
			// do something else or we can do this...
			while (session.bRunning)
			{
				Sleep(10); // sleep 10 milliseconds - don't starve the CPU!

				if(session.progressPct != 255) // 255 is an error condition!
					printf("Conversion progress = %ld %%\n", session.progressPct);
			}

			myThread.join(); // terminate the thread

			if(session.result && (session.eLastError == EXSErrorCodes::eXS_ERRORCODE_OK))
			{
				// conversion was successful!
				assert(session.progressPct == 100);
			}
			else
			{
				// something went wrong! Check the error code session.eLastError.
			}
		}
		// else the thread failed to run!?!
	}
	// End example threaded usage
*/

extern "C" XSCORE_API XBOOL X4_ConvertSessionPair(const char* sessionLeftX4R, const char* sessionRightX4R, const char* folderXSN, uint8_t * progressPct);
// Similar to X4_ConvertSession. Expects two paired sessions for the left and right insoles.
// The two X4R session names will share a common -XTK#### token.
// 
// The resulting single XSN file is named after the left insole session file.
//
// See X4_ConvertSession for example usage.

#endif // WIP