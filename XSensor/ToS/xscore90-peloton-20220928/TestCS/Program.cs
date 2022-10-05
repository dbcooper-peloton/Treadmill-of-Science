using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using xsensor;
using SENSORPID = System.UInt64;

namespace TestCS
{
    class Program
    {
        static void Main(string[] args)
        {
            // See Test.cpp for more details on what this code is doing.

            // construct an instance of the DLL
            XSCore90 xs = new XSCore90();

            // Initialize the XS Core library
            xbool bThread = xbool.TRUE;
            if (XSCore90.XS_InitLibrary(bThread) != xbool.TRUE)
                return;

            ushort major = 0, minor = 0, build = 0, revision = 0;
            XSCore90.XS_GetVersion(ref major, ref minor, ref build, ref revision);

            Console.WriteLine("DLL Version: " + major.ToString() + "." + minor.ToString() + "." + build.ToString() + "." + revision.ToString());

            bool bRemoteSessionTest = false;

            if (!bRemoteSessionTest)
            {
                // Enumerate and configure all wired X4 sensors (and X3 wired)
                RunLocalSession(true);

                // Enumerate and configure all wireless X4 sensors (and X3 wired)
                //RunLocalSession(true, true);

                // Enumerate and configure all wired X3 sensors
                //RunLocalSession(false);
            }
            else // run a remote session test for X4 insole sensors
            {
                //	Enumerate and configure the first found insole sensor and start or 
                //  stop a remote session.
                RunRemoteSessionSingle(false);

                //	Enumerate and configure the first left/right insole sensors and start or 
                //  stop a remote session.
                //RunRemoteSessionPair(false);
            }

            // deallocate resources and memory
            XSCore90.XS_ExitLibrary();

            Console.WriteLine("Press a key to exit...");
            Console.ReadKey();
        }

        static void RunLocalSession(bool allowX4, bool wirelessX4 = false)
        {
            Console.WriteLine("Running local session test");
            Console.WriteLine("Setting calibration cache...");

            // Set the calibration cache folder to some writable location on the PC
            XSCore90.XS_SetCalibrationFolder("e:\\CalCache");
            // Set this path to a folder on the computer. Be sure the path has write/create access
            // This holds the downloaded calibration file and speeds up subsequent XS_AutoConfig calls.

            uint framesPerMinute = 10 * 60; // 10 Hz

            // IMU is only suported by X4 insole sensors!
            bool enableIMU = false;

            if (allowX4)
            {
                // Use the following call with xbool.TRUE if you are connecting to the sensors wirelessly - they must already be paired in Windows
                XSCore90.XS_SetAllowX4Wireless(wirelessX4 ? xbool.TRUE : xbool.FALSE); // wireless X4

                // Use the following call with xbool.TRUE if you are connecting to the sensors over USB wire
                XSCore90.XS_SetAllowX4((!wirelessX4) ? xbool.TRUE : xbool.FALSE);
                // If you use BOTH XS_SetAllowX4Wireless(xbool.TRUE) and XS_SetAllowX4(xbool.TRUE) at the same time, the DLL will favour USB wired over wireless.

                // Use 8 bit mode when transmitting over Bluetooth wireless to ensure higher framerates
                XSCore90.XS_SetX4Mode8Bit(wirelessX4 ? xbool.TRUE : xbool.FALSE);
                XSCore90.XS_SetSampleAverageCount(4); // 4 or 8 for X4 sensors. smaller number is faster, but with slightly worse signal-to-noise

                framesPerMinute = 75 * 60; // 75 Hz

                // if you're testing X4 insole sensor, you can use this
                if(enableIMU)
                    XSCore90.XS_SetEnableIMU(xbool.TRUE); // if we want IMU data with each frame

                // note: if an X3 sensor is attached it will also be enumerated
            }
            // else - by default X4 is off ... so only X3 sensors will be picked up
            else
            {
                enableIMU = false; // not supported by X3

                // 1, 2, 4, 8 for X3 sensors. smaller number is faster, but with slightly worse signal-to-noise
                XSCore90.XS_SetSampleAverageCount(1);
            }


            // we'll work in PSI for this demo
            EPressureUnit ePressureUnits = EPressureUnit.ePRESUNIT_PSI;
            XSCore90.XS_SetPressureUnit(ePressureUnits);


            Console.WriteLine("Enumerating sensors and configuring...");
#if (true)
            // Automatically create a sensor configuration with all connected sensors using your preferred pressure units.
            if (XSCore90.XS_AutoConfig(ePressureUnits) != xbool.TRUE)
            {
                Console.WriteLine("No sensors configured. XS_GetLastErrorCode()=[" + XSCore90.XS_GetLastErrorCode().ToString() + "] and XS_GetLastEnumState()=[" + XSCore90.XS_GetLastEnumState().ToString() + "]");

                //Console.WriteLine("AutoConfig failed. Please check error codes.\nEXSErrorCodes=%s.\nEEnumerationError=%s", XSCore90.XS_GetLastErrorCodeAsString(), XSCore90.XS_GetLastEnumStateAsString());
                return;
            }
#else // or do the same but construct an XSN file that can be viewed in the XSENSOR desktop software.
	        if (XSCore90.XS_AutoConfigXSN("e:\\mySession.xsn", ePressureUnits) != xbool.TRUE)
	        {
		        //Console.WriteLine("AutoConfig failed. Please check error codes.\nEXSErrorCodes=%s.\nEEnumerationError=%s", XS_GetLastErrorCodeAsString(), XS_GetLastEnumStateAsString());
		        return;
	        }
#endif

            // query the configured sensors for their combined pressure range. (Different sensors may have different ranges.)
            float nMinPressure = 0.0f, nMaxPressure = 0.0f;
            XSCore90.XS_GetConfigInfo(ePressureUnits, ref nMinPressure, ref nMaxPressure);

            Console.WriteLine("Configured sensors are calibrated from " + nMinPressure.ToString("0.000") + " to " + nMaxPressure.ToString("0.000") + " " + ePressureUnits.ToString());

            // Fetch some details for each configured sensor
            uint nNbrConfigured = XSCore90.XS_ConfigSensorCount();
            for (uint nSensor = 0; nSensor < nNbrConfigured; nSensor++)
            {
                // fetch the sensor identifer
                SENSORPID spid = XSCore90.XS_ConfigSensorPID(nSensor);

                // fetch the sensor name
                uint bufferSize = 0;
                XSCore90.XS_GetSensorName(spid, ref bufferSize, null);
                var sb = new StringBuilder((int)bufferSize);
                XSCore90.XS_GetSensorName(spid, ref bufferSize, sb);
                string sensorName = sb.ToString();

                Console.WriteLine("Sensor #" + nSensor.ToString() + ": " + sensorName + " S" + XSCore90.XS_GetSerialFromPID(spid).ToString());


                // fetch the dimensions of a single cell
                float nSenselWidthCM = 0, nSenselHeightCM = 0;
                XSCore90.XS_GetSenselDims(spid, ref nSenselWidthCM, ref nSenselHeightCM);

                // Fetch the row and column counts for this sensor
                ushort rows = 0, columns = 0;
                XSCore90.XS_GetSensorDimensions(spid, ref rows, ref columns);

                Console.WriteLine("Width: " + (nSenselWidthCM * (float)columns).ToString() + "cm  Height: " + (nSenselHeightCM * (float)rows).ToString() + "cm");
            }


            // determine if a calibration file was set for all of the sensors.
            // Calibration files are stored on the sensors. These convert the raw electronic reading into a pressure reading.
            xbool bIsDataCalibrated = XSCore90.XS_IsCalibrationConfigured();

            if (bIsDataCalibrated != xbool.TRUE)
            {
                Console.WriteLine("Failed to download all calibration files. The sampled values are in RAW units only!");
            }

            Console.WriteLine("Opening connection to sensors...");

            // open a connection to the configured sensors
            if (XSCore90.XS_OpenConnection(framesPerMinute) == xbool.TRUE) // 75 Hz or 4500 frames per minute
            {
                bool bThreaded = XSCore90.XS_IsConnectionThreaded() == xbool.TRUE;

                Console.WriteLine("XS_OpenConnection succeeded.");
                Console.WriteLine("XS_IsConnectionThreaded = " + (bThreaded ? "yes" : "no"));

                ushort year = 0;
                byte month = 0, day = 0;
                byte hour = 0, minute = 0, second = 0;
                ushort millisecond = 0;
                if (bThreaded)
                    XSCore90.XS_GetSampleTimestampUTC(ref year, ref month, ref day, ref hour, ref minute, ref second, ref millisecond);

                byte prevminute = minute;
                byte prevsecond = second;
                ushort prevmillisecond = millisecond;
                ushort nNoSampleDelay = 0;

                // Attempt to collect a number of frames
                int nMaxFrames = 1; // fetch one frame
                int nFrame = 0;

                while (nFrame < nMaxFrames)
                {
                    // Tell the DLL to sample the configured sensors and generate a new frame
                    if (XSCore90.XS_Sample() == xbool.TRUE)
                    {
                        if (bThreaded)
                        {
                            // If we're running in a threaded mode, then XS_Sample is an asynchronous call.
                            // This means there may or may not be a new sample ready. In this case we must check
                            // the timestamp of the current sample to see if it has changed.

                            XSCore90.XS_GetSampleTimestampUTC(ref year, ref month, ref day, ref hour, ref minute, ref second, ref millisecond);

                            if ((minute != prevminute) || (second != prevsecond) || (millisecond != prevmillisecond))
                            {
                                // time has changed, thus we have a new frame
                                nFrame++;
                                prevminute = minute;
                                prevsecond = second;
                                prevmillisecond = millisecond;
                                nNoSampleDelay = 0;
                            }
                            else
                            {
                                System.Threading.Thread.Sleep(10);

                                nNoSampleDelay += 10;
                                if (nNoSampleDelay > 2000) // 2 seconds
                                    break; // too long of a delay between frames
                            }

                            // If the library was initialized with XS_InitLibrary(xbool.TRUE),
                            // then XS_Sample will return immediately if there is a queued sample.
                        }
                        else
                        {
                            // If we're not running in a threaded mode, then XS_Sample blocks until a new sample is available.
                            nFrame++;

                            XSCore90.XS_GetSampleTimestampUTC(ref year, ref month, ref day, ref hour, ref minute, ref second, ref millisecond);

                            // If the library was initialized with XS_InitLibrary(xbool.FALSE), 
                            // then XS_Sample will block until a sample is collected - or it will timeout
                        }


                        // Retrieve the pressure data from the DLL's buffers

                        // retrieve the data for each sensor
                        for (uint nSensor = 0; nSensor < nNbrConfigured; nSensor++)
                        {
                            SENSORPID spid = XSCore90.XS_ConfigSensorPID(nSensor);

                            // Fetching the dimensions of the sensor. These don't change, so this can be called outside the loop.
                            ushort nNbrRows = 0, nNbrColumns = 0;
                            XSCore90.XS_GetSensorDimensions(spid, ref nNbrRows, ref nNbrColumns);

                            // compute the number of sensels in the sample
                            uint nCellCount = (uint)(nNbrRows * nNbrColumns);
                            if (nCellCount == 0)
                                continue; // this should never occur

                            // Allocate a buffer to hold the pressure.
                            // Normally you would allocate this buffer only once and outside this loop!
                            // You can allocate one buffer for each sensor, or one large buffer to hold all sensors.
                            float[] pressureMap = new float[nCellCount];

                            // Fetch the pressure readings collected by the XS_Sample() call and place them in the buffer.
                            // Do this for each sensor in the configuration.
                            if (XSCore90.XS_GetPressureSafe(spid, nCellCount, pressureMap) == xbool.TRUE)
                            {
                                if (enableIMU)
                                {
                                    float qx = 0, qy = 0, qz = 0, qw = 0;
                                    float ax = 0, ay = 0, az = 0;
                                    float gx = 0, gy = 0, gz = 0;

                                    // IMU data is refreshed with each new frame from the insole sensor
                                    if (XSCore90.XS_GetIMU(spid, ref qx, ref qy, ref qz, ref qw, ref ax, ref ay, ref az, ref gx, ref gy, ref gz) == xbool.TRUE)
                                    {
                                        Console.WriteLine("IMU = {" +
                                                "\tqx = " + qx.ToString() + "" +
                                                "\tqy = " + qy.ToString() + "" +
                                                "\tqz = " + qz.ToString() + "" +
                                                "\tqw = " + qw.ToString() + "" +
                                            "}");
                                    }
                                }

                                bool bDisplayNumbers = true;
                                DumpFrame(pressureMap, nNbrColumns, nNbrRows, bDisplayNumbers, nMinPressure, nMaxPressure);
                            }
                        }
                    }
                    else
                    {
                        // This is an odd condition. Perhaps the sensor became disconnected.
                        Console.WriteLine("XS_Sample failed.  ERRORCODE=" + XSCore90.XS_GetLastErrorCode().ToString());

                        System.Threading.Thread.Sleep(10); // sleep 10 milliseconds, don't stave the CPU

                        nNoSampleDelay += 10;
                        if (nNoSampleDelay > 2000) // 2 seconds
                            break; // too long of a delay between frames
                    }
                } // next frame

                // Close all connections to the sensors.
                XSCore90.XS_CloseConnection();
            }
            else
            {
                Console.WriteLine("XS_OpenConnection failed. ERRORCODE=" + XSCore90.XS_GetLastErrorCode().ToString());
            }
        }

        // ----------------------------------------------------------------------
        //	RunRemoteSessionSingle
        // 
        //	Enumerate and configure the first found insole sensor and start or 
        //  stop a remote session.
        // ----------------------------------------------------------------------

        static void RunRemoteSessionSingle(bool wirelessX4)
        {
            Console.WriteLine("Running remote session single insole test");
            Console.WriteLine("Setting calibration cache...");

            // Set the calibration cache folder to some writable location on the PC
            // This folder is also used for tracking X4 state (x4tokens.bin)
            XSCore90.XS_SetCalibrationFolder("e:\\CalCache");
            // Set this path to a folder on the computer. Be sure the path has write/create access
            // This holds the downloaded calibration file and speeds up subsequent XS_AutoConfig calls.

            // Use the following call with xbool.TRUE if you are connecting to the sensors wirelessly - they must already be paired in Windows
            XSCore90.XS_SetAllowX4Wireless(wirelessX4 ? xbool.TRUE : xbool.FALSE); // wireless X4

            // Use the following call with xbool.TRUE if you are connecting to the sensors over USB wire
            XSCore90.XS_SetAllowX4((!wirelessX4) ? xbool.TRUE : xbool.FALSE);
            // If you use BOTH XS_SetAllowX4Wireless(xbool.TRUE) and XS_SetAllowX4(xbool.TRUE) at the same time, the DLL will favour USB wired over wireless.

            // Use 8 bit mode when transmitting over Bluetooth wireless to ensure higher framerates
            XSCore90.XS_SetX4Mode8Bit(wirelessX4 ? xbool.TRUE : xbool.FALSE);
            XSCore90.XS_SetSampleAverageCount(4); // 4 or 8 for X4 sensors. smaller number is faster, but with slightly worse signal-to-noise

            XSCore90.XS_SetPressureUnit(EPressureUnit.ePRESUNIT_PSI);

            // Be care with XS_EnumSensors as it will interrupt any will not discovery any new X4's if they're in the middle of a remote recording!

            // Normally enumeration will disrupt X4 remote recordings. We'll turn that off here.
            XSCore90.XS_SetAllowEnumInterruptX4Remote(xbool.FALSE);

            // scan for available sensors - can take a while as it tries all known connections
            uint sensorCount = XSCore90.XS_EnumSensors();
            if (sensorCount == 0)
            {
                Console.WriteLine("No available sensors found for remote test.");
                return;
            }

            bool bFound = false;
            SENSORPID spid = 0;
            xbool bFootSensor = xbool.FALSE;
            xbool bLeftFoot = xbool.FALSE;

            // we'll connect to the first X4 we find
            for (uint sensor = 0; sensor < sensorCount; sensor++)
            {
                spid = XSCore90.XS_EnumSensorPID(sensor);

                if ((XSCore90.XS_IsX4FootSensor(spid, ref bFootSensor, ref bLeftFoot) == xbool.TRUE) && (bFootSensor == xbool.TRUE))
                {
                    bFound = true;

                    // fetch the sensor name
                    uint bufferSize = 0;
                    XSCore90.XS_GetSensorName(spid, ref bufferSize, null);
                    var sb = new StringBuilder((int)bufferSize);
                    XSCore90.XS_GetSensorName(spid, ref bufferSize, sb);
                    string sensorName = sb.ToString();

                    Console.WriteLine("Found X4 foot sensor [" + sensorName + "]");
                    break;
                }
            }

            if (!bFound)
            {
                Console.WriteLine("No X4 foot sensors found with active SD cards");
                return;
            }

            // Open a connection to the X4
            if (XSCore90.X4_OpenRemote(spid) != xbool.TRUE)
            {
                Console.WriteLine("X4 remote command failed with error [" + XSCore90.XS_GetLastErrorCode().ToString() + "]");
                return;
            }

            // check if a recording is in progress
            xbool remoteRecording = xbool.FALSE;
            if (XSCore90.X4_IsRemoteRecording(spid, ref remoteRecording) == xbool.TRUE)
            {
                Console.WriteLine("X4 remote recording session is " + ((remoteRecording == xbool.TRUE) ? "active" : "not active"));

                if (remoteRecording == xbool.TRUE)
                {
                    Console.WriteLine("Stopping X4 remote recording");

                    XSCore90.X4_StopRemoteRecording(spid);

                    // now close the connection
                    XSCore90.X4_CloseRemote(spid);
                    return;
                }
            }
            else
            {
                Console.WriteLine("X4 remote command failed with error [" + XSCore90.XS_GetLastErrorCode().ToString() + "]");
            }


            // attempt session download and conversion


            Console.WriteLine("Prepping for X4 remote recording");

            float frameRateHz = 40.0f;
            if (XSCore90.X4_StartRemoteRecording(spid, frameRateHz) == xbool.TRUE)
            {
                Console.WriteLine("X4 remote recording started");

                System.Threading.Thread.Sleep(100);  // give it some time to generate some frames

                Console.WriteLine("Fetching preview frame");

                if (XSCore90.X4_SampleRemote(spid) == xbool.TRUE)
                {
                    // Fetching the dimensions of the sensor. These don't change, so this can be called outside the loop.
                    ushort nNbrRows = 0, nNbrColumns = 0;
                    XSCore90.XS_GetSensorDimensions(spid, ref nNbrRows, ref nNbrColumns);

                    // compute the number of sensels in the sample
                    uint nCellCount = (uint)(nNbrRows * nNbrColumns);

                    // Allocate a buffer to hold the pressure.
                    // Normally you would allocate this buffer only once and outside this loop!
                    // You can allocate one buffer for each sensor, or one large buffer to hold all sensors.
                    float[] pressureMap = new float[nCellCount];

                    // Fetch the pressure readings collected by the XS_Sample() call and place them in the buffer.
                    // Do this for each sensor in the configuration.
                    if (XSCore90.XS_GetPressureSafe(spid, nCellCount, pressureMap) == xbool.TRUE)
                    {
                        bool bDisplayNumbers = true;

                        float nMinPressure = 0;
                        float nMaxPressure = 200.0f;
                        XSCore90.X4_GetRemoteSampleRange(spid, XSCore90.XS_GetPressureUnit(), ref nMinPressure, ref nMaxPressure);

                        DumpFrame(pressureMap, nNbrColumns, nNbrRows, bDisplayNumbers, nMinPressure, nMaxPressure);
                    }
                }
            }
            else
            {
                Console.WriteLine("X4 remote command failed with error [" + XSCore90.XS_GetLastErrorCode().ToString() + "]");
            }

            // close the connection
            XSCore90.X4_CloseRemote(spid);
        }


        // ----------------------------------------------------------------------
        //	RunRemoteSessionPair
        // 
        //	Enumerate and configure the first left/right insole sensors and start or 
        //  stop a remote session.
        // ----------------------------------------------------------------------

        static void RunRemoteSessionPair(bool wirelessX4)
        {
            Console.WriteLine("Running remote session insole pair test");
            Console.WriteLine("Setting calibration cache...");

            // Set the calibration cache folder to some writable location on the PC
            // This folder is also used for tracking X4 state (x4tokens.bin)
            XSCore90.XS_SetCalibrationFolder("e:\\CalCache");
            // Set this path to a folder on the computer. Be sure the path has write/create access
            // This holds the downloaded calibration file and speeds up subsequent XS_AutoConfig calls.

            // Use the following call with xbool.TRUE if you are connecting to the sensors wirelessly - they must already be paired in Windows
            XSCore90.XS_SetAllowX4Wireless(wirelessX4 ? xbool.TRUE : xbool.FALSE); // wireless X4

            // Use the following call with xbool.TRUE if you are connecting to the sensors over USB wire
            XSCore90.XS_SetAllowX4((!wirelessX4) ? xbool.TRUE : xbool.FALSE);
            // If you use BOTH XS_SetAllowX4Wireless(xbool.TRUE) and XS_SetAllowX4(xbool.TRUE) at the same time, the DLL will favour USB wired over wireless.

            // Use 8 bit mode when transmitting over Bluetooth wireless to ensure higher framerates
            XSCore90.XS_SetX4Mode8Bit(wirelessX4 ? xbool.TRUE : xbool.FALSE);
            XSCore90.XS_SetSampleAverageCount(4); // 4 or 8 for X4 sensors. smaller number is faster, but with slightly worse signal-to-noise

            XSCore90.XS_SetPressureUnit(EPressureUnit.ePRESUNIT_PSI);

            // Be care with XS_EnumSensors as it will interrupt any will not discovery any new X4's if they're in the middle of a remote recording!

            // Normally enumeration will disrupt X4 remote recordings. We'll turn that off here.
            XSCore90.XS_SetAllowEnumInterruptX4Remote(xbool.FALSE);

            // scan for available sensors - can take a while as it tries all known connections
            uint sensorCount = XSCore90.XS_EnumSensors();
            if (sensorCount == 0)
            {
                Console.WriteLine("No available sensors found for remote test.");
                return;
            }


            SENSORPID spid = 0;  // sensor pad id
            SENSORPID spidLeft = 0;
            SENSORPID spidRight = 0;
            xbool bFootSensor = xbool.FALSE;
            xbool bLeftFoot = xbool.FALSE;

            // we'll connect to the first X4 we find
            for (uint sensor = 0; sensor < sensorCount; sensor++)
            {
                spid = XSCore90.XS_EnumSensorPID(sensor);

                if ((XSCore90.XS_IsX4FootSensor(spid, ref bFootSensor, ref bLeftFoot) == xbool.TRUE) && (bFootSensor == xbool.TRUE))
                {
                    // fetch the sensor name
                    uint bufferSize = 0;
                    XSCore90.XS_GetSensorName(spid, ref bufferSize, null);
                    var sb = new StringBuilder((int)bufferSize);
                    XSCore90.XS_GetSensorName(spid, ref bufferSize, sb);
                    string sensorName = sb.ToString();

                    Console.WriteLine("Found X4 foot sensor [" + sensorName + "]");

                    if (bLeftFoot == xbool.TRUE)
                    {
                        if (spidLeft == 0)
                            spidLeft = spid;
                    }
                    else //if (!bLeftFoot)
                    {
                        if (spidRight == 0)
                            spidRight = spid;
                    }
                }
            }


            if ((spidLeft == 0) || (spidRight == 0))
            {
                Console.WriteLine("No X4 pair of insole sensors found.");
                return;
            }

            // we have a pair!
            // Open a connection to the X4
            if (XSCore90.X4_OpenRemote(spidLeft) != xbool.TRUE)
            {
                Console.WriteLine("Could not open a connection to the left insole: error [" + XSCore90.XS_GetLastErrorCode().ToString() + "]");
                return;
            }

            if (XSCore90.X4_OpenRemote(spidRight) != xbool.TRUE)
            {
                XSCore90.X4_CloseRemote(spidLeft);
                Console.WriteLine("Could not open a connection to the right insole: error [" + XSCore90.XS_GetLastErrorCode().ToString() + "]");
                return;
            }

            // check if a recording is in progress
            xbool remoteRecordingLeft = xbool.FALSE;
            xbool remoteRecordingRight = xbool.FALSE;

            if (XSCore90.X4_IsRemoteRecording(spidLeft, ref remoteRecordingLeft) != xbool.TRUE)
                Console.WriteLine("X4 remote command failed with error [" + XSCore90.XS_GetLastErrorCode().ToString() + "]");

            if (XSCore90.X4_IsRemoteRecording(spidRight, ref remoteRecordingRight) != xbool.TRUE)
                Console.WriteLine("X4 remote command failed with error [" + XSCore90.XS_GetLastErrorCode().ToString() + "]");

            Console.WriteLine("X4 (left insole) remote recording session is " + ((remoteRecordingLeft == xbool.TRUE) ? "active" : "not active"));
            Console.WriteLine("X4 (right insole) remote recording session is " + ((remoteRecordingRight == xbool.TRUE) ? "active" : "not active"));

            if ((remoteRecordingLeft == xbool.TRUE) && (remoteRecordingRight != xbool.TRUE))
            {
                Console.WriteLine("Stopping left X4 remote recording");
                XSCore90.X4_StopRemoteRecording(spidLeft);
                XSCore90.X4_CloseRemote(spidLeft);
                XSCore90.X4_CloseRemote(spidRight);
                return;
            }
            else if ((remoteRecordingLeft != xbool.TRUE) && (remoteRecordingRight == xbool.TRUE))
            {
                Console.WriteLine("Stopping right X4 remote recording");
                XSCore90.X4_StopRemoteRecording(spidRight);
                XSCore90.X4_CloseRemote(spidLeft);
                XSCore90.X4_CloseRemote(spidRight);
                return;
            }

            // both are recording
            if ((remoteRecordingLeft == xbool.TRUE) && (remoteRecordingRight == xbool.TRUE))
            {
                Console.WriteLine("Stopping X4 remote recording");
                XSCore90.X4_StopRemotePairRecording(spidLeft, spidRight);

                // now close the connection
                XSCore90.X4_CloseRemote(spidLeft);
                XSCore90.X4_CloseRemote(spidRight);
                return;
            }


            // attempt session download and conversion
            uint minutes = 0;
            float frameRateHz = 40.0f;

            if (XSCore90.X4_GetRemoteDuration(spidLeft, frameRateHz, ref minutes) == xbool.TRUE)
                Console.WriteLine("X4 left insole has " + minutes.ToString() + " minutes available @ " + frameRateHz.ToString("0.0") + " Hz for recording.");

            if (XSCore90.X4_GetRemoteDuration(spidRight, frameRateHz, ref minutes) == xbool.TRUE)
                Console.WriteLine("X4 right insole has " + minutes.ToString() + " minutes available @ " + frameRateHz.ToString("0.0") + " Hz for recording.");

            Console.WriteLine("Prepping for X4 remote paired recording");

            if (XSCore90.X4_StartRemotePairRecording(spidLeft, spidRight, 40.0f) == xbool.TRUE)
            {
                Console.WriteLine("X4 remote paired recording started");
            }
            else
            {
                Console.WriteLine("X4 remote paired command failed with error [" + XSCore90.XS_GetLastErrorCode().ToString() + "]");
            }


            // close the connections
            XSCore90.X4_CloseRemote(spidLeft);
            XSCore90.X4_CloseRemote(spidRight);
        }


        static void DumpFrame(float[] pressureMap, ushort nNbrColumns, ushort nNbrRows, bool bDisplayNumbers, float nMinPressure, float nMaxPressure)
        {
            // display the data as a set of numbers
            if (bDisplayNumbers)// display the pressure numbers
            {
                float nMax = 0.0f, nAvg = 0.0f;
                int cellCount = 0;

                for (ushort nRow = 0; nRow < nNbrRows; nRow++)
                {
                    for (ushort nColumn = 0; nColumn < nNbrColumns; nColumn++)
                    {
                        float pressure = pressureMap[(uint)nRow * (uint)nNbrColumns + (uint)nColumn];

                        if (pressure < 0)
                        {
                            Console.Write("---- ");
                            continue; // this is a dead sensel (typically for foot sensors this is a cell out side the sensing area)
                        }

                        cellCount++; // for averaging

                        if (pressure > nMax)
                            nMax = pressure;

                        nAvg += pressure;

                        Console.Write(pressure.ToString("0.00 "));
                    }
                    Console.WriteLine("");
                }

                if (cellCount > 1)
                    nAvg /= (float)cellCount;

                Console.WriteLine("AVG = " + nAvg.ToString() + "\tMAX = " + nMax.ToString());
                Console.WriteLine("");
            }
            else
            {
                // display the data as an ASCII image
                ProcessFrame(pressureMap, nNbrRows, nNbrColumns, nMinPressure, nMaxPressure);
            }
        }
        static void ProcessFrame(float[] pressureMap, ushort wRows, ushort wColumns, float nMinPressure, float nMaxPressure)
        {
            string isobarMapDarkToLight = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?_+~<>i!lI;:,\"^`'. ";

            int nNbrIsobars = isobarMapDarkToLight.Length;
            int nIsobar = 0;

            for (ushort wRow = 0; wRow < wRows; wRow++)
            {
                Console.Write("\t");
                for (ushort wColumn = 0; wColumn < wColumns; wColumn++)
                {
                    float pressure = pressureMap[wRow * wColumns + wColumn]; // use this calculations to traverse the array in a 2D manner

                    if (pressure < 0) // this means this cell is not in the grid (a dead sensel)
                    {
                        Console.Write("-");
                        continue;
                    }

                    nIsobar = GetIsobar(pressure, nMinPressure, nMaxPressure, nNbrIsobars);
                    // convert the pressure to an ascii isobar
                    Console.Write(isobarMapDarkToLight[nIsobar].ToString());

                }

                Console.WriteLine("");
            }
            Console.WriteLine("");

        } // end ProcessFrame

        static int GetIsobar(float xpressure, float xminPressure, float xmaxPressure, int xbarCount)
        {
            return (((xpressure) >= (xmaxPressure)) ? (int)((xbarCount) - 1) : (((xpressure) < (xminPressure)) ? 0 : ((int)(((xpressure) - (xminPressure)) * ((xbarCount) - 2) / ((xmaxPressure) - (xminPressure)) + 1))));
        }

    }
}
