#pragma once

/* XSNReader.h -- interface of the 'XSNReader' XSN file parser library
  version 8.0.146 2021-03-11

  Copyright (C) 2013-2021  XSENSOR Technology Corporation. All rights reserved.

  This software is provided 'as-is', without any express or implied
  warranty.  In no event will XSENSOR Technology Corporation be held liable
  for any damages arising from the use of this software.

  Permission is granted to any Licensee of the XSENSOR PRO 8 software
  to use this software (XSNReader.dll and XSNReader64.dll) for any
  non-commercial purpose, subject to the following terms and restrictions:

  1. The Licensee agrees that this software is covered by the terms and
     restrictions of the Software License Agreement covering the XSENSOR PRO 8 Software.

*/

#ifdef XSNReader_EXPORTS
	#define XSNREADER_API __declspec(dllexport)
#else
	#define XSNREADER_API __declspec(dllimport)
	#ifdef _X64TARGET
		#pragma message("Statically linking 64 bit XSNReader64.lib in XSNReader.h")
		#pragma comment(lib, "XSNReader64.lib")
	#else
		#pragma message("Statically linking 32 bit XSNReader.lib in XSNReader.h")
		#pragma comment(lib, "XSNReader.lib")
	#endif
#endif

// 8 bits
#include <stdint.h> // for uint8_t, uint16_t, uint32_t

#include <wtypes.h> // for BSTR - C# compatible string

enum EXSNPressureUnit
{
	eXSNPRESUNIT_MMHG = 0,	// millimeters of mercury
	eXSNPRESUNIT_INH2O,		// inches of water
	eXSNPRESUNIT_PSI,		// pounds/sq.inch
	eXSNPRESUNIT_KPA,		// kilopascals
	eXSNPRESUNIT_KGCM2,		// kgf/cm^2
	eXSNPRESUNIT_ATM,		// atmospheres
	eXSNPRESUNIT_NCM2,		// newtons/cm^2
	eXSNPRESUNIT_MBAR,		// millibars
	eXSNPRESUNIT_NM2,		// Newton/meter^2
	eXSNPRESUNIT_GCM2,		// grams/cm^2
	eXSNPRESUNIT_BAR,		// bar

	eXSNPRESUNIT_RAW = 255
};

// force/load units
enum EXSNForceUnit
{
	eXSNFORCEUNIT_UNKNOWN = 0,	//  raw pressure values?
	eXSNFORCEUNIT_NEWTONS = 1,	// newtons
	eXSNFORCEUNIT_KGF = 2,		// kilograms of force
	eXSNFORCEUNIT_LBF = 10,		// pound-force
};

enum EXSNReaderErrorCodes
{
	eXSN_ERRORCODE_OK,							// Function ran normally

	eXSN_ERRORCODE_LIBRARY_NOT_INITIALIZED,		// The DLL library has not been initialized

	eXSN_ERRORCODE_INVALID_XSN,					// LoadSession failed because the session is not a valid xsensor file
	eXSN_ERRORCODE_INVALID_VERSION,				// LoadSession failed because the session is a valid xsensor file, but the version is not supported.
	eXSN_ERRORCODE_UNSUPPORTED_SENSOR,			// The reader DLL does not support the sensor model found in the XSN.

	eXSN_ERRORCODE_NOSESSION,					// The operation failed because no session has been loaded.
	eXSN_ERRORCODE_EMPTYSESSION,				// The operation failed because there are no frames in this session

	eXSN_ERRORCODE_BADPARAMETER_OUTOFRANGE,		// a parameter is out of range
	eXSN_ERRORCODE_BADPARAMETER_NULL,			// null parameter - pass in a variable/buffers address

	eXSN_ERRORCODE_MEMORYALLOCATION_FAILED,		// the system seems to be running low on memory, or the DLL could not allocate some memory
};

// ===========================================================================
//	Configuration functions
// ===========================================================================

extern "C" XSNREADER_API EXSNReaderErrorCodes XSN_GetLastErrorCode();
// Retrieves the last error code.  Check this value when a function reports a failure.  (see enum EXSNErrorCodes below).


// ===========================================================================
//	Library initialization/deinitialization
// ===========================================================================

extern "C" XSNREADER_API bool XSN_InitLibrary();
extern "C" XSNREADER_API bool XSN_InitLibraryEx(const void* pReserved=0);
// Initialize the library.  This must be the first call to the Library
// Pass in 0 or NULL to the XSN_InitLibraryEx function or just call XSN_InitLibrary()

extern "C" XSNREADER_API bool XSN_ExitLibrary();
// Uninitializes the library, freeing all allocated resources.  This should be the last call to the Library

extern "C" XSNREADER_API uint16_t XSN_GetLibraryMajorVersion();
// returns the library's major version number

extern "C" XSNREADER_API uint16_t XSN_GetLibraryMinorVersion();
// returns the library's minor version number


// ===========================================================================
// Session Initialization
// ===========================================================================

extern "C" XSNREADER_API bool XSN_LoadSessionU(const wchar_t* szSession);
extern "C" XSNREADER_API bool XSN_LoadSession(const char* szSession);
// loads an xsensor data file
// Resets the pressure units to the base ones used in the session file
// Returns true (non-zero) if the load is successful

extern "C" XSNREADER_API bool XSN_CloseSession();
// unloads the current session file. Frees the file handle so the file can be accessed elsewhere.


// ===========================================================================
//	Session Configuration
// ===========================================================================

extern "C" XSNREADER_API uint32_t XSN_FrameCount();
// Returns the number of frames in the session file.

extern "C" XSNREADER_API uint8_t XSN_PadCount();
// Returns the number of pads in the session file

// used for C# to fetch info about the sensors
extern "C" XSNREADER_API bool XSN_GetPadInfo(uint8_t pad, BSTR* sModel, BSTR* sProductID, BSTR* sSerial);

// used for C, C++ and Python
extern "C" XSNREADER_API bool XSN_GetPadInfoEx(uint8_t pad, 
	wchar_t* sModel, uint32_t& nModelLength, 
	wchar_t* sProductID, uint32_t& nProductLength, 
	wchar_t* sSerial, uint32_t& nSerialLength);
// Pass in null for the strings to retrieve the size of the buffer
// If the buffers are 0 or NULL, the length of the required buffer(in wchar_t count) is calculated
// and returned in the length parameters.

extern "C" XSNREADER_API bool XSN_GetPadSenselDims(uint8_t pad, float& widthCM, float& heightCM);
// width and height of a single cell (a sensel) in centimetres

extern "C" XSNREADER_API bool XSN_IsFootSensor(uint8_t pad, bool& bLeftSensor);
// Returns true if the pad is a foot sensor.  bLeftSensor = false when its a right foot sensor.

extern "C" XSNREADER_API uint16_t XSN_Rows(uint8_t pad);
// Returns the number of rows associated with the pad index (0 based index)

extern "C" XSNREADER_API uint16_t XSN_Columns(uint8_t pad);
// Returns the number of columns associated with the pad index (0 based index)

extern "C" XSNREADER_API EXSNPressureUnit XSN_GetPressureUnits();
// Returns the pressure unit format of the pressure values

extern "C" XSNREADER_API bool XSN_SetPressureUnits(EXSNPressureUnit eUnits);
// Sets the pressure unit format of the pressure values

extern "C" XSNREADER_API EXSNForceUnit XSN_GetForceUnits();
// Returns the load or force units that correspond to the current pressure units


extern "C" XSNREADER_API float XSN_GetMaxPressure();
// Returns the maximum pressure the file was calibrated for. (If raw, then 65534.0f)

extern "C" XSNREADER_API float XSN_GetMinPressure();
// Returns the minimum pressure the file was calibrated for. (If raw, then 0.0f)
// Values below this pressure are considered uncalibrated.

extern "C" XSNREADER_API float XSN_GetZeroThreshold();
// Returns the file's zero threshold pressure. Values below this threshold are considered to be zero.

extern "C" XSNREADER_API bool XSN_GetGeneralNotes(BSTR* sNotes);
// Retrieves any general notes set in the session (if any) (Use this for C#)

extern "C" XSNREADER_API bool XSN_GetGeneralNotesEx(wchar_t* sNotes, uint32_t& nNotesLength);
// Retrieves any general notes set in the session(if any) (Use this for C/Python)
// Pass in null or None for the string buffer to retrieve the length of the buffer (in wchar_t counts)

extern "C" XSNREADER_API bool XSN_GetFrameNotes(BSTR* sNotes);
// Retrieves any notes specific to the current frame (Use this for C#)

extern "C" XSNREADER_API bool XSN_GetFrameNotesEx(wchar_t* sNotes, uint32_t& nNotesLength);
// Retrieves any notes specific to the current frame (Use this for C/Python)
// Pass in null or None for the string buffer to retrieve the length of the buffer (in wchar_t counts)


// ===========================================================================
//	Frame navigation
// ===========================================================================

extern "C" XSNREADER_API bool XSN_StepToFrame(uint32_t nFrame);
// Steps to the frame (1 based index)

extern "C" XSNREADER_API uint32_t XSN_GetFrameID();
// Retrieves the current frame ID (or zero if no frame)

extern "C" XSNREADER_API uint16_t XSN_GetSessionID();
// The start-stop session to which the current frame belongs (zero if no frame)
// Use this to detect recording gaps due to recording stoppage and restart


extern "C" XSNREADER_API bool XSN_GetTimeStampUTC(uint16_t& nYear, uint16_t& nMonth, uint16_t& nDay, uint16_t& nHour, uint16_t& nMinute, uint16_t& nSecond, uint16_t& nMilliseconds);
extern "C" XSNREADER_API bool XSN_GetTimeStampUTCuS(uint16_t& nYear, uint16_t& nMonth, uint16_t& nDay, uint16_t& nHour, uint16_t& nMinute, uint16_t& nSecond, uint16_t& nMilliseconds, uint16_t& wMicrosecs);
// Retrieves the timestamp associated with the current frame - in UTC format


// ===========================================================================
//	Pressure Map Access
// ===========================================================================

// This version takes a preallocated buffer whose size is specified with dataSize - used for C# wrapper
extern "C" XSNREADER_API bool XSN_GetPressure(uint8_t pad, uint32_t dataSize, float data[]);
// dataSize is the number of elements in the data[] array
// dataSize should be at least dataSize = XSN_Rows(pad) * XSN_Columns(pad). The function will fail if its not.

extern "C" XSNREADER_API bool XSN_GetPressureMapEx(uint8_t pad, float* pPressureMap, uint32_t& nMapElementCount);
// Retrieves the pressure map. nMapElementCount is the number of element required for the pressure map.
// Set pPressureMap to 0 or null to just retrieve the nMapElementCount.
// nMapElementCount = XSN_Rows(pad) * XSN_Columns(pad);
// Use with C/Python


extern "C" XSNREADER_API float* XSN_GetPressureMap(uint8_t pad);
// Creates and returns a buffer containing the pressure map information for the targeted pad from the current frame.
// pad is a 0 based index
// Returns NULL or 0 if no valid frame.
// The caller must call FreePressureMap with the returned pointer to properly free up this memory.

extern "C" XSNREADER_API bool XSN_FreePressureMap(float* pPressureMap);
// Frees the memory that was returned via a GetPressureMap() call

extern "C" XSNREADER_API bool XSN_CopyPressureMap(uint8_t pad, float* pPressureMap);
// Similar to GetPressureMap, except that the caller must allocate the memory for a buffer and maintains ownership over the memory.
// pad is a 0 based index
// The caller is responsible for ensuring the pPressureMap buffer is large enough


// ===========================================================================
//	Pressure Map Statistics
// ===========================================================================

// These functions return the statistics for the current pressure map.
// If there is an error, -1.0f is returned for all stats functions. Call XSN_GetLastErrorCode() if that occurs.
// The pressure readings below the zero threshold are treated as zero.
// The zero threshold should be in the same units as XSN_GetPressureUnits().

extern "C" XSNREADER_API float XSN_GetStatAvgPressure(uint8_t pad, float nZeroThreshold);
// Return the average pressure of the pressure map. Zero pressure cells are not included in the statistic.

extern "C" XSNREADER_API float XSN_GetStatPeakPressure(uint8_t pad, float nZeroThreshold);
// Return the peak/maximum pressure on the pressure map.

extern "C" XSNREADER_API float XSN_GetStatMinPressure(uint8_t pad, float nZeroThreshold);
// Return the minimum pressure on the pressure map. Zero pressure cells are not included in the statistic.

extern "C" XSNREADER_API float XSN_GetStatContactAreaCM(uint8_t pad, float nZeroThreshold);
// Return the area (centimeters) of the pressure map with pressure at or above the zero threshold.
// Zero pressure cells are not included in the statistic.

extern "C" XSNREADER_API float XSN_GetStatEstimatedLoad(uint8_t pad, float nZeroThreshold);
// Return the estimated load (force) applied to the sensor.
// Zero pressure cells are not included in the statistic.
// Call XSN_GetForceUnits() to determine the units of the load statistic.


extern "C" XSNREADER_API bool XSN_GetCOP(uint8_t pad, float nZeroThreshold, float& column, float& row);
// Computes the center of pressure (COP) and returns its column and row coordinates.
// Returns negative coordinates if there is a problem. Call XSN_GetLastErrorCode() if that occurs.
//
// The center of pressure calculation ignores pressure which is below the zero threshold.
// Row coordinates are from 1 to XSN_Rows()
// Column coordinates are from 1 to XSN_Columns()
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


/* Programmer Note:

   To avoid having to manage the frame buffer memory, yet still benefit from
   the memory efficiency of XSN_CopyPressureMap, do the following:

   uint8_t pad = 0;

   // The first time you fetch a pressure map, call XSN_GetPressureMap and save the pointer
   float* pPressureMap1 = XSN_GetPressureMap(pad);

   // subsequently, call XSN_CopyPressureMap using the saved pointer.
   XSN_CopyPressureMap(pad,pPressureMap1);

   // remember to free this pointer once you're done with it
   XSN_FreePressureMap(pPressureMap1);

   If you have multiple pads, then each one should have its own pressure map buffer.
*/

