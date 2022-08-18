using System;
using System.Runtime.InteropServices;

// https://docs.microsoft.com/en-us/cpp/dotnet/how-to-wrap-native-class-for-use-by-csharp?view=vs-2019

namespace xsensor
{
    public enum EXSNPressureUnit
    {
        eXSNPRESUNIT_MMHG = 0,  // millimeters of mercury
        eXSNPRESUNIT_INH2O,     // inches of water
        eXSNPRESUNIT_PSI,       // pounds/sq.inch
        eXSNPRESUNIT_KPA,       // kilopascals
        eXSNPRESUNIT_KGCM2,     // kgf/cm^2
        eXSNPRESUNIT_ATM,       // atmospheres
        eXSNPRESUNIT_NCM2,      // newtons/cm^2
        eXSNPRESUNIT_MBAR,      // millibars
        eXSNPRESUNIT_NM2,       // Newton/meter^2
        eXSNPRESUNIT_GCM2,      // grams/cm^2
        eXSNPRESUNIT_BAR,       // bar

        eXSNPRESUNIT_RAW = 255
    };

    public enum EXSNForceUnit
    {
        eXSNFORCEUNIT_UNKNOWN = 0,  //  raw pressure values?
        eXSNFORCEUNIT_NEWTONS = 1,  // newtons
        eXSNFORCEUNIT_KGF = 2,      // kilograms of force
        eXSNFORCEUNIT_LBF = 10,     // pound-force
    };


    public enum EXSNReaderErrorCodes
    {
        eXSN_ERRORCODE_OK,                          // Function ran normally

        eXSN_ERRORCODE_LIBRARY_NOT_INITIALIZED,     // The DLL library has not been initialized

        eXSN_ERRORCODE_INVALID_XSN,                 // LoadSession failed because the session is not a valid xsensor file
        eXSN_ERRORCODE_INVALID_VERSION,             // LoadSession failed because the session is a valid xsensor file, but the version is not supported.

        eXSN_ERRORCODE_NOSESSION,                   // The operation failed because no session has been loaded.
        eXSN_ERRORCODE_EMPTYSESSION,                // The operation failed because there are no frames in this session

        eXSN_ERRORCODE_BADPARAMETER_OUTOFRANGE,     // a parameter is out of range
        eXSN_ERRORCODE_BADPARAMETER_NULL,           // null parameter - pass in a variable/buffers address

        eXSN_ERRORCODE_MEMORYALLOCATION_FAILED,     // the system seems to be running low on memory, or the DLL could not allocate some memory
    };

    public class XSN
    {
        // =============================================
        // DLL ENTRY
        // =============================================

        // ===========================================================================
        //	Library initialization/deinitialization
        // ===========================================================================

        const String DLL_TARGET = "XSNReader64";

        // If Windows is 64 bit, use "XSNReader64"
        // If Windows is 32 bit, use "XSNReader"

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern EXSNReaderErrorCodes XSN_GetLastErrorCode();
        // Retrieves the last error code.  Check this value when a function reports a failure.  (see enum EXSNErrorCodes below).

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool XSN_InitLibrary();
        // Initialize the library.  This must be the first call to the Library

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool XSN_ExitLibrary();
        // Uninitializes the library, freeing all allocated resources.  This should be the last call to the Library

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern ushort XSN_GetLibraryMajorVersion();
        // returns the library's major version number

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern ushort XSN_GetLibraryMinorVersion();
        // returns the library's minor version number


        // ===========================================================================
        // Session Initialization
        // ===========================================================================

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern bool XSN_LoadSessionU(string sSession);
        // loads an xsensor data file
        // Resets the pressure units to the base ones used in the session file
        // Returns true (non-zero) if the load is successful

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool XSN_CloseSession();
        // unloads the current session file. Frees the file handle so the file can be accessed elsewhere.

        // ===========================================================================
        //	Session Configuration
        // ===========================================================================

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern uint XSN_FrameCount();
        // Returns the number of frames in the session file.

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern byte XSN_PadCount();
        // Returns the number of pads in the session file

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern bool XSN_GetPadInfo(byte pad, [MarshalAs(UnmanagedType.BStr)] out string sModel, [MarshalAs(UnmanagedType.BStr)] out string sProductID, [MarshalAs(UnmanagedType.BStr)] out string sSerial);

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool XSN_GetPadSenselDims(byte pad, ref float widthCM, ref float heightCM);
        // width and height of a single cell (a sensel) in centimetres

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool XSN_IsFootSensor(byte pad, ref bool bLeftSensor);
        // Returns xTRUE if the pad is a foot sensor.  bLeftSensor = false when its a right foot sensor.

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern ushort XSN_Rows(byte pad);
        // Returns the number of rows associated with the pad index (0 based index)

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern ushort XSN_Columns(byte pad);
        // Returns the number of rows associated with the pad index (0 based index)

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern EXSNPressureUnit XSN_GetPressureUnits();
        // Returns the pressure unit format of the pressure values

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool XSN_SetPressureUnits(EXSNPressureUnit eUnits);
        // Sets the pressure unit format of the pressure values

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern EXSNForceUnit XSN_GetForceUnits();
        // Returns the load or force units that correspond to the current pressure units


        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern float XSN_GetMaxPressure();
        // Returns the maximum pressure the file was calibrated for. (If raw, then 65534.0f)

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern float XSN_GetMinPressure();
        // Returns the maximum pressure the file was calibrated for. (If raw, then 0.0f)

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern float XSN_GetZeroThreshold();
        // Returns the file's zero threshold pressure. Values below this threshold are considered to be zero.


        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern bool XSN_GetGeneralNotes([MarshalAs(UnmanagedType.BStr)] out string sNotes);
        // Retrieves any general notes set in the session (if any)

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl, CharSet = CharSet.Unicode)]
        public static extern bool XSN_GetFrameNotes([MarshalAs(UnmanagedType.BStr)] out string sNotes);
        // Retrieves any notes specific to the current frame


        // ===========================================================================
        //	Frame navigation
        // ===========================================================================
        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool XSN_StepToFrame(uint nFrame);
        // Steps to the frame (1 based index)

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern uint XSN_GetFrameID();
        // Retrieves the current frame ID (or zero if no frame)

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern ushort XSN_GetSessionID();
        // The start-stop session to which the current frame belongs (zero if no frame)
        // Use this to detect recording gaps due to recording stoppage and restart

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool XSN_GetTimeStampUTC(ref ushort nYear, ref ushort nMonth, ref ushort nDay, ref ushort nHour, ref ushort nMinute, ref ushort nSecond, ref ushort nMilliseconds);

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool XSN_GetTimeStampUTCuS(ref ushort nYear, ref ushort nMonth, ref ushort nDay, ref ushort nHour, ref ushort nMinute, ref ushort nSecond, ref ushort nMilliseconds, ref ushort wMicrosecs);
        // Retrieves the timestamp associated with the current frame - in UTC format


        // ===========================================================================
        //	Pressure Map Access
        // ===========================================================================

        // This version takes a preallocated buffer whose size is specified with dataSize - used for C# wrapper
        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern bool XSN_GetPressure(byte pad, uint dataSize, float[] data);
        // EXSNPressureUnit eUnits will convert the pressure to the desired units
        // dataSize is the number of elements in the data[] array
        // dataSize should be at least dataSize = XSN_Rows(pad) * XSN_Columns(pad). The function will fail if its not.

        // ===========================================================================
        //	Pressure Map Statistics
        // ===========================================================================

        // These functions return the statistics for the current pressure map.
        // If there is an error, -1.0f is returned for all stats functions. Call XSN_GetLastErrorCode() if that occurs.
        // The pressure readings below the zero threshold are treated as zero.
        // The zero threshold should be in the same units as XSN_GetPressureUnits().

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern float XSN_GetStatAvgPressure(byte pad, float zeroThreshold);
        // Return the average pressure of the pressure map. Zero pressure cells are not included in the statistic.

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern float XSN_GetStatPeakPressure(byte pad, float zeroThreshold);
        // Return the peak/maximum pressure on the pressure map.

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern float XSN_GetStatMinPressure(byte pad, float zeroThreshold);
        // Return the minimum pressure on the pressure map. Zero pressure cells are not included in the statistic.

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern float XSN_GetStatContactAreaCM(byte pad, float zeroThreshold);
        // Return the area (centimeters) of the pressure map with pressure at or above the zero threshold.
        // Zero pressure cells are not included in the statistic.

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern float XSN_GetStatEstimatedLoad(byte pad, float zeroThreshold);
        // Return the estimated load (force) applied to the sensor.
        // Zero pressure cells are not included in the statistic.
        // Call XSN_GetForceUnits() to determine the units of the load statistic.

        [DllImport(DLL_TARGET, CallingConvention = CallingConvention.Cdecl)]
        public static extern float XSN_GetCOP(byte pad, float zeroThreshold, ref float column, ref float row);
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

    }

} // xsensor namespace