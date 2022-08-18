/* XSCore90.cs -- wrapper interface of the 'XSCore90' sensor engine.
  
  Copyright (C) 2010-2022  XSENSOR Technology Corporation. All rights reserved.

  This software is provided 'as-is', without any express or implied
  warranty.  In no event will XSENSOR Technology Corporation be held liable
  for any damages arising from the use of this software.
*/

using System;
using System.Runtime.InteropServices;
using System.Text; // for StringBuilder

// alias for the sensor's unique ID - 64 bits
using SENSORPID = System.UInt64;

// example C to C# struct for other projects
/*
[StructLayout(LayoutKind.Sequential)]
public struct Vertex
{
    public float x;
    public float y;
    public float z;
    public int ID;
}
*/

namespace xsensor
{
    // boolean type to help with marshalling from the C dll
    public enum xbool : byte { FALSE = 0, TRUE };

    public enum EPressureUnit
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

    public enum EXSErrorCodes
    {
        eXS_ERRORCODE_OK,							// Function ran normally

        eXS_ERRORCODE_BADPARAMETER_OUTOFRANGE,		// a parameter is out of range
        eXS_ERRORCODE_BADPARAMETER_NULL,			// null parameter - pass in a variable/buffers address
        eXS_ERRORCODE_BADPARAMETER_INVALID_SENSOR_PID,	// either the PID is pad, or the sensor was not configured

        eXS_ERRORCODE_CALFILE_LOADFAILED,			// calibration file failed to load - likely the file wasn't found
        eXS_ERRORCODE_CALFILE_DOESNOTMATCHSENSOR,	// the calibration file does not match the sensor

        eXS_ERRORCODE_CONFIGURATION_NOTCOMPLETE,	// Call XS_ConfigComplete() to complete the sensor configuration.
        eXS_ERRORCODE_CONFIGURATION_NOSENSORS,		// no sensors have been added to the sample config via XS_AddSensorToConfig(), or could not be added
        eXS_ERRORCODE_CONFIGURATION_FAILCREATEXSN,	// Could not create the XSN file. Check that the path is valid and the location can be written too.

        eXS_ERRORCODE_SENSORS_SENSORNOTFOUND,		// either the sensor isn't enumerated, or the PID is invalid
        eXS_ERRORCODE_SENSORS_RAWONLY,				// XS_GetPressure() called, but no calibration files have been loaded.  Only raw data is available.
        eXS_ERRORCODE_SENSORS_NOSAMPLE,				// XS_Sample() has not been called yet, or it has not succeeded in retrieving a sample

        eXS_ERRORCODE_SENSORS_CONNECTIONLOST,		// XS_Sample failed because a sensor was disconnected or USB power reset
        eXS_ERRORCODE_SENSORS_SAMPLETIMEOUT,		// XS_Sample failed because the sensor timed out while reading
        eXS_ERRORCODE_SENSORS_SAMPLEFAILED,			// XS_Sample failed for reasons unknown

        eXS_ERRORCODE_SENSORS_NOCONNECTION,			// Calling XS_Sample() without first calling to XS_OpenConnection()?
        eXS_ERRORCODE_SENSORS_CONNECTFAILED,		// It's possible that one of the sensors has become disconnected.  Check connections.

        eXS_ERRORCODE_MEMORYALLOCATION_FAILED,		// the system seems to be running low on memory, or the DLL could not allocate some memory

        eXS_ERRORCODE_LIBRARY_NOT_INITIALIZED,		// The DLL library has not been initialized

        eXS_ERRORCODE_AUTOCONFIG_SENSORNOTFOUND,	// no sensors found during enumeration - please check XS_GetLastEnumState()

        eXS_ERRORCODE_COULDNOTCREATECAPTUREFILE,	// Could not create the target capture file

        eXS_ERRORCODE_SIMFILE_LOADFAIL,				// A problem occured while loading the simulation file.  The path might be incorrect, or the file cannot be opened.  (Try loading it in the XSENSOR desktop software.)
        eXS_ERRORCODE_SIM_FUNCTION_NA,				// The DLL function is not available or does nothing while in simulation mode.

        eXS_ERRORCODE_SIM_CALIBRATED_ONLY,			// The simulation only supports calibrated (pressure) data
        eXS_ERRORCODE_SIM_RAW_ONLY,					// The simulation only supports raw (non-pressure) data

        eXS_ERRORCODE_MANCAL_FUNCTION_NOTSET,		// The manaul calibration state is not set, which this function requires.
        eXS_ERRORCODE_MANCAL_FUNCTION_NA,			// The DLL function is not available or does nothing while in manual calibration mode.
        eXS_ERRORCODE_CALIBRATION_AUTOCACHE,		// This calibration function is disabled while the calibration auto-cache is enabled via XS_SetCalibrationFolder.
    };

    // this is a bit mask - any number of these bits might be set
    public enum EEnumerationError
    {
        eENUMERROR_OK = 0x00000000,	// no errors detected

        eENUMERROR_NOSPKSDETECTED = 0x00000001,	// no SPKS appear in the computer
        eENUMERROR_OPENDEVICEFAIL = 0x00000002,	// The SPK could not be opened with CreateFile
        eENUMERROR_OPENDEVICEFAIL_PROCESSLOCK = 0x00000004,	// The SPK could not be opened because some other process has it opened
        eENUMERROR_HIDDEVICEENUMFAIL = 0x00000008,	// The HID device enumerate failed - very low level

        eENUMERROR_MISSINGCON = 0x00000010,	// The SPK is not connected to a sensor pad
        eENUMERROR_MISSINGDLLCODE = 0x00000020,	// The sensor does not have a DLL code
        eENUMERROR_MISMATCHEDDLLCODE = 0x00000040,	// The sensor's DLL code does not match this DLL
        eENUMERROR_MISSINGPROFILE = 0x00000080,	// The sensors profile is not supported by this DLL

        eENUMERROR_MISSINGCHILDSPKS = 0x00000100,	// This multi-SPK sensor is missing SPKS ports 2 to N
        eENUMERROR_MISSINGPARENTSPK = 0x00000200,	// This multi-SPK sensor is missing SPK on port 1
        eENUMERROR_MISMATCHEEDFIRMWARE = 0x00000400,	// This multi-SPK sensor must the same firmware on each SPK
        eENUMERROR_MISMATCHEDSPKTYPES = 0x00000800,	// This multi-SPK sensor must the same SPK types on each port (either XS PRO, or just XS)

        eENUMERROR_CONNECTIONSENSE = 0x00001000,	// This sensor pad is not properly plugged into the SPK - or there is a hardware problem with the sensor
        eENUMERROR_CONREQUIRESNEWERFIRMWARE = 0x00002000,	// The sensor pad requires SPK(s) with firmware 1.3 or better

        // the rest of the bits are reserved
    };

    
    public class XSCore90
    {
        // replace "XSCore90" with "XSCore90x64" if you're using the 64 bit dll

        // ===========================================================================
        //	Library initialization/deinitialization
        // ===========================================================================

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern EXSErrorCodes XS_GetLastErrorCode();
        // Retrieves the last error code.  Check this value when a function reports a failure.  (see enum EXSErrorCodes below).

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_InitLibrary(xbool bThreadMode);
        // Initialize the XS software engine.  This must be the first call to the XS Library
        // Use bThreadMode if you want the DLL to sample independently of the call to XS_Sample.
        // Otherwise set to boolFALSE to have finer control over the sample rate.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_ExitLibrary();
        // Uninitializes the XS software engine, freeing all allocated resources.  This should be the last call to the XS Library

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetVersion(ref ushort major, ref ushort minor, ref ushort build, ref ushort revision);
        // fetches the DLL version - major.minor.build.revision

        // ===========================================================================
        //	Sensor Enumeration and Information
        // ===========================================================================

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern uint XS_EnumSensors();
        // Scan the computer for available sensors

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern void XS_SetAllowFastEnum(xbool bAllow);
        // When enabled, the DLL skips looking for new sensors and only attempts to talk to sensors it already knows about.
        // Use this when you've found a sensor, but lost its connection and want to rescan for it without the delay of looking
        // for new sensors.
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetAllowFastEnum();


        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern EEnumerationError XS_GetLastEnumState();
        // Retrieves the EEnumerationError error state.  This value is only valid after a call to XS_EnumSensors

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern uint XS_EnumSensorCount();
        // Returns a count of the number of sensors found during the EnumSensors() call.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern SENSORPID XS_EnumSensorPID(uint nEnumIndex);
        // Returns the sensor PRODUCT ID at the indexed location of the enumerated sensors list.  The index is zero based.
        // The SENSORPID is 64 bit value.  If the value is 0, then the function call failed.  (Likely an index out of array bounds condition.)

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern ushort XS_GetSerialFromPID(SENSORPID spid);
        // returns a sensor's 4 digit serial number.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetSensorDimensions(SENSORPID spid, ref ushort nRows, ref ushort nColumns);
        // returns the sensors sensel dimensions


        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_GetSensorName(SENSORPID spid, ref uint bufferSize, StringBuilder sensorName);
        // If sensorName is NULL, the size of the required buffer (in bytes) is calculated and returned in bufferSize.
        /* example C# call
            uint bufferSize = 0;
            XS_GetSensorName(spid, ref bufferSize, null);
            var sb = new StringBuilder((int)bufferSize);
            XS_GetSensorName(spid, ref bufferSize, sb);
            string sensorName = sb.ToString();
         */

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetSenselDims(SENSORPID spid, ref float nWidthCM, ref float nHeightCM);
        // returns a single sensel's physical dimensions in centimetres. Only usable after a sensor configuration is created.


        // Is this an X4 sensor?
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_IsX4Sensor(SENSORPID spid);

        // Sets bFootSensor to xTRUE if the sensor is an X4 foot sensor. Sets bLeftFoot to xTRUE if its a left foot sensor, and xFALSE for right sensors
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_IsX4FootSensor(SENSORPID spid, ref xbool bFootSensor, ref xbool bLeftFoot);

        // ===========================================================================
        //	Calibration file management
        // ===========================================================================

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_SetCalibrationFolder(string calibrationFolder);
        // When the DLL is provided with a folder for caching calibration files, it will automatically
        // manage downloading and selection of an appropriate calibration file.
        // While enabled, the other calibration file functions are not enabled.
        //
        // Typically this is the best option for managing calibration files
        //
        // Alternatively you may use the following functions for direct management
        // of a sensor's calibration files:
        // XS_DownloadCalibrations; XS_GetCalibrationName; XS_GetCalibrationInfo; XS_GetCalibrationInfoEx

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern uint  XS_DownloadCalibrations(SENSORPID spid, string calibrationFolder);
        // Downloads the calibration files stored on the sensor and saves them to a folder.
        // Returns number of files downloaded. There may be 0, 1 or more calibration files on the sensor.  
        // Usually if there are more then 1, then each file represents a different calibrated pressure range.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_GetCalibrationName(uint nCalIndex, ref uint bufferSize, StringBuilder calName);
        // After calling XS_DownloadCalibrations(), call this function to retrieve the name of the downloaded calibration file.
        // If calName is null, the size of the required buffer (in bytes) is calculated and returned in bufferSize.
        // 'nCalIndex' is a zero based index.
        // NOTE: this function only applies to the XS_DownloadCalibrations() call.  It does not work with XS_AddSensorToConfig_AutoCal().
        /* example C# call
            uint bufferSize = 0;
            XS_GetCalibrationName(nCalIndex, ref bufferSize, null);
            var sb = new StringBuilder((int)bufferSize);
            XS_GetCalibrationName(nCalIndex, ref bufferSize, sb);
            string calFileName = sb.ToString();
         */

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_GetCalibrationInfo(string sCalibrationFile, byte nPressureUnits, ref float nMinPressure, ref float nMaxPressure);
        // Scans the calibration file, and returns the maximum pressure (in the provided pressure units - see EPressureUnit)
        // szCalibrationFile is the full path to the cal file on disk.  eg: c:\\CalFiles\\MyCalFile.xsc

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_GetCalibrationInfoEx(string sCalibrationFile, ref SENSORPID spid);
        // Retrieve the SENSORPID from this calibration file
        // szCalibrationFile is the full path to the cal file on disk.  eg: c:\\CalFiles\\MyCalFile.xsc


        // ===========================================================================
        //	AUTOMATIC Sensor Configuration
        //
        //	These functions simplify the process of configuring any connected sensors.
        // ===========================================================================

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_AutoConfig(EPressureUnit pressureUnits, float nTargetPressure = -1.0f);
        // creates a configuration using all sensors attached to the system.  Downloads any calibration files into memory and uses them.
        // Please note that while this is the simplest way to configure the sensors, it is also the slowest because the calibration download takes a fair bit of time.
        // pass in nTargetPressure = -1.0f to select the sensor's default calibration range

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_AutoConfigXSN(string XSNFullPath, EPressureUnit pressureUnits, float nTargetPressure = -1.0f);
        // Similar to XS_AutoConfig(), but also creates a standalone XSN session file.
        // The szXSNFile path and file name must be fully specified. eg: "c:\MySessions\Test.xsn".


        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_AutoConfigByDefault();
        // Auto-configure using the default settings for the found sensors. Same as XS_AutoConfig(ePRESUNIT_RAW,-1.0f). Added for Python support.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_AutoConfigByDefaultXSN(string XSNFullPath);
        // Auto-configure using the default settings for the found sensors. Same as XS_AutoConfig(ePRESUNIT_RAW,-1.0f). Added for Python support.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_AutoConfig_SingleSensor(string calFileFullPath);

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_AutoConfig_SingleSensorXSN(string xsnFileFullPath, string calFileFullPath);
        // Wraps all of the enumeration and configuration into a single call.
        // Optionally provide a path to a calibration file to override any calibration downloads.
        // ie: XS_AutoConfig_SingleSensor(L"d:\\MyCalFiles\\PX100363605_20121022_1151.xsc");
        // This only works if there is a single sensor present.

        // ===========================================================================
        //	MANUAL Sensor Configuration
        //
        //	These functions give better control over the configuration of any connected
        //	sensors.
        // ===========================================================================

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_NewSensorConfig();
        // Prepares the DLL to create a configuration of sensors.  Remove any existing configured sensors.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_NewSensorConfigXSN(string xsnFileFullPath);
        // Similar to XS_NewSensorConfig(), but also creates a standalone XSN session file.
        // The szXSNFile path and file name must be fully specified. eg: "c:\MySessions\Test.xsn".

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_AddSensorToConfig(SENSORPID spid, string calFileFullPath);
        // Adds a sensor to the sensor configuration.  Sensors in the configuration are sampled when XS_Sample() is called.
        // A calibration file can be specified here.  If szCalibrationFile is 0, then only raw data is collected.
        // All sensors in the configuration must have calibration files, otherwise only raw values are collected.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_AddSensorToConfig_AutoCalByDefault(SENSORPID spid);

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_AddSensorToConfig_AutoCal(SENSORPID spid, EPressureUnit nPressureUnits, float nTargetMaxPressure);
        // nTargetMaxPressure - pass in -1.0 to default to the cal file's max pressure
        // Adds a sensor to the sensor configuration.  Sensors in the configuration are sampled when XS_Sample() is called.
        // Attempts to download a calibration file from the sensor and use it.
        // If nPressureUnits is raw, then it uses the first calibration file it finds, otherwise it attempts to match the desired maximum pressure
        // Note: Downloading can be a bit slow.

        // When finished adding sensors to the configuration, call this function to initialize it and prepare for calling XS_OpenConnection()
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_ConfigComplete();

        // Returns xTRUE if the DLL has a sensor configuration
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_HasConfig();

        // Closes any open connection and releases the configuration (including any XSN file).
        // Subsequent calls to XS_OpenConnection will fail until a new config is created.
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_ReleaseConfig();

        // ===========================================================================
        //	Sensor Configuration Information
        // ===========================================================================

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern SENSORPID XS_ConfigSensorPID(uint nConfigIndex);
        // Returns the sensor PRODUCT ID at the indexed location of the configured sensors list.  The index is zero based.
        // Call XS_NewSensorConfig+XS_AddSensorToConfig+XS_ConfigComplete or XS_AutoConfigByDefault() before calling this function.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern uint XS_ConfigSensorCount();
        // returns the number of configured sensors

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_IsCalibrationConfigured();
        // Returns boolTRUE if the configuration is setup for calibrated data.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetConfigInfo(EPressureUnit pressureUnits, ref float nMinPressure, ref float nMaxPressure);
        // After the configuration is complete, call this to check the pressure range of the sensor.
        // nPressureUnits - the pressure units in which the minimum and maximum pressures are returned. (See EPressureUnits below)
        // If operating in RAW mode (i.e.: no calibration file specified), then nPressureUnits is ignored.

        // ===========================================================================
        //	Other Settings
        // ===========================================================================

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern void XS_SetPressureUnit(EPressureUnit pressureUnits);
        // Sets the calibrated data's pressure units.  This can be changed at any time.
        // The default value is kg/cm^2 (ePRESUNITS_KGCM2).

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern EPressureUnit XS_GetPressureUnit();
        // Returns the current pressure units (see EPressureUnit).

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern void XS_SetReadTimeout(uint TimeoutSeconds);
        // Sets the sample function's timeout period in seconds.
        //
        // If the software loses connection to a sensor, it tries to re-open the connection
        // for this length of time.
        //
        // 5 seconds is default

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern uint XS_GetReadTimeout();
        // returns the sample timeout period in seconds


        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern void XS_SetOverlapMode(xbool bOverlap);
        // When sampling with two or more sensors and if the sensors are physically
        // overlapping, turn this mode on to ensure there is no electrical interference between
        // the sensors.
        //
        // Note this causes each sensor to be sampled in series (instead of in parallel), thus
        // there is often a reduction in net sampling speed.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetOverlapMode();
        // returns boolTRUE when Overlap mode is on.  Overlap mode is off by default.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern void XS_SetAllowWireless(xbool bAllow);
        // allows use of the X3 wireless series
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetAllowWireless();

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern void XS_SetAllowX4(xbool bAllow);
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetAllowX4();
        // allows use of the X4 sensor series (wired)

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern void XS_SetAllowX4Wireless(xbool bAllow);
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetAllowX4Wireless();
        // allows use of the X4 sensor series (wireless)


        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern void XS_SetX4Mode8Bit(xbool b8BitMode);
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetX4Mode8Bit();
        // set the X4 in 8 bit mode (lower precision, but faster wireless transmit)

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_HasHardwareIMU(SENSORPID spid);
        // determines if the sensor has IMU capability

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_SetEnableIMU(xbool bEnable);
        // enable IMU packets if available - does this for all configured sensors. Must call before the OpenConnection

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetEnableIMU();
        // return true if IMU is enabled for the current configuration


        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern void XS_SetStreamingMode(xbool bStreaming);
        // If you are sampling below 10 Hz, set this mode to xbool.FALSE, otherwise set to xbool.TRUE for better sample rates

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetStreamingMode();
        // returns boolTRUE if streaming mode is on, boolFALSE otherwise.  This is off by default.        

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern void XS_SetSampleAverageCount(short nCount);
        // Set the number of readings the hardware will perform on each sensel.
        // Valid numbers are 1, 2, 4, 8 and 16
        //
        // This averaging occurs within the sensor's DPS hardware. Higher cycles lead to slower
        // frame rates, but may produce more accurate readings.
        //
        // X4 sensors can only run at 4 and 8 cycles. X4 foot sensors run fastest with 4 cycles.
        //
        // This value can only be set before calling any of the XS_AutoConfig* functions, or XS_ConfigComplete()
        // Typically you don't need to set this as the sensor is normally programmed with an expected default.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern short XS_GetSampleAverageCount();
        // returns the number of readings the hardware will perform on each sensel.  Each reading is
        // averaged together.  Default is 1 which means no averaging.  Hardware supports: 1,2,4,8,16 samples being averaged.


        // ===========================================================================
        //	Connection management
        // ===========================================================================

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_OpenConnection(uint nThreadedFramesPerMinute = 0);
        //
        // Opens the sensors in the sample configuration and readies them for sampling.
        //
        // Call this only after a call to XS_ConfigComplete() or XS_AutoConfig*()
        //
        // nThreadedFramesPerMinute
        //	- When using the DLL in threaded mode (ie: XS_InitLibrary(boolTRUE)),
        //    this specifies the target frame rate in frames per minute. eg: 600 FPM = 10 Hz
        //
        //    The actual rate may be slower depending on the sensor configuration and
        //    the PC's USB subsystem. This field is ignored when XS_InitLibrary(boolFALSE)
        //	  is called.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_IsConnectionOpen();
        // returns boolTRUE if the connection is open.
        //
        // Typically this function returns boolFALSE when a sensor is disconnected, or
        // the sensor is in use by another program.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_CloseConnection();
        // closes the connection - this releases the sensors and allows other applications to talk to them.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_IsConnectionThreaded();
        // Returns xTRUE if the connection is open and the connection is running in an asynchronous threaded mode.


        // ===========================================================================
        //	Sampling functions
        // ===========================================================================

        // Returns the threshold below which pressure is zeroed.
        // a return of -1.0f indicates the function failed. Check XS_GetLastErrorCode.
        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern float XS_GetNoiseThreshold();

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_SetNoiseThreshold(float nThreshold);
        // Sets a pressure threshold, below which any readings are zeroed. The threshold is applied
        // to all configured sensors.
        //
        // The default threshold is normally the lowest calibrated pressure of all configured sensors.
        //
        // nThreshold - The threshold must be in the same pressures units as is returned by XS_GetPressureUnit()

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_Sample();
        // Ask the sensor(s) to record a new sample (a pressure map) to an internal buffer.
        // Use XS_GetPressure() to retrieve the pressure map from the internal buffer.
        //
        // When using the library in a threaded mode, this call returns immediately. 
        // However, the internal buffer may or may not have a new sample as it only updates
        // when a new one is available. Check the timestamp to see if it has changed.
        //
        // When not using threaded mode, this call blocks until a sample is recorded or
        // a read timeout occurs.

        // Fetch the timestamp (UTC time) of the last sample obtained from a call to XS_Sample().

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetSampleTimestampUTC(ref ushort year, ref byte month, ref byte day, ref byte hour, ref byte minute, ref byte second, ref ushort millisecond);
        // Same as XS_GetSampleTime(), but separates the date/time components.
        // Fetch the timestamp components (UTC time). month (1-12), day (1-31). Hour is (0-23), minute and second (0-59), millisecond (0-999)

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetSampleTimestampExUTC(
	        ref ushort year, ref byte month, ref byte day, 
	        ref byte hour, ref byte minute, ref byte second, ref ushort millisecond, ref ushort microsecond, bool bAsLocalTime);
        // includes microseconds when supported by the sensor hardware. This version allows conversion of the timestamp to the local timezone.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetPressureSafe(SENSORPID spid, uint nDataSize, float[] data);
        // Retrieves the calibrated sample data for a single sensor from the DLL's internal buffer and populates the supplied output buffer.
        // ( The internal buffer is only populated and changed via a call to XS_Sample() )
        // The pressure readings are in the units set by XS_SetPressureUnit() or XS_AutoConfig()
        //
        // pData - the output buffer should be large enough to hold (rows X columns) elements of sizeof(uint16_t).
        //		Where rows and columns are the dimensions of the sensor.
        //		The array is organized in a typical row-major order. IE:The first N values in the array correspond 
        //		to the first row, where N is the number of columns.
        //

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetRawSafe(SENSORPID spid, uint nDataSize, ushort[] data);
        // Similar to XS_GetPressureSafe(), except it takes an array of uint16_t and returns uncalibrated raw 16 bit values from the sensor.

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetIMU(SENSORPID spid,
                                                ref float qx, ref float qy, ref float qz, ref float qw,
                                                ref float ax, ref float ay, ref float az,
                                                ref float mx, ref float my, ref float mz);
        // retrieves any IMU data if present for the current sample

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
        public static extern xbool XS_GetHardwareFrameState(SENSORPID spid, ref uint sequence, ref uint ticks);
        // Retrieves the hardware frame header state. 'sequence' increments (and wrapsaround) for each frame. 'ticks' is milliseconds for X4
        // returns xFALSE if there is no hardware state, or an error has occured

        /* internal functions

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_OpenConnectionX4Script(string szConfigScript, uint frame);

                [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
                public static extern xbool XS_SetDiagnosticIMU(xbool bEnable);
                // enable retrieval of the calibrated magnetometer triad

                [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl)]
                public static extern xbool XS_GetDiagnosticIMU();
                // return true if IMU diagnostic mode is enabled for the current configuration

        [DllImport("XSCore90", CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern xbool XS_OverrideProfile(string profileFullPath);

        */
        public static void Test()
        {
            xbool bThread = xbool.TRUE;
            XS_InitLibrary(bThread);

            ushort major = 0;
            ushort minor = 0;
            ushort build = 0;
            ushort revision = 0;

            XS_GetVersion(ref major, ref minor, ref build, ref revision);

            XS_ExitLibrary();
        }

    }
}