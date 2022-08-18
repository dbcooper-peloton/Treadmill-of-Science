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

            // NOTE: If you're testing this demo and you get teh fol
            //
            // System.DllNotFoundException: 'Unable to load DLL 'XSCore90':
            //
            // Be sure to copy XSCore90.dll into 
            //   TestCS\bin\debug


            ushort major = 0;
            ushort minor = 0;
            ushort build = 0;
            ushort revision = 0;
            XSCore90.XS_GetVersion(ref major, ref minor, ref build, ref revision);

            // RunTest - enumerate and configure all attached sensors for a selected pressure range, and take some samples
            RunTest();

            // deallocate resources and memory
            XSCore90.XS_ExitLibrary();
        }

        static void RunTest()
        {
            // Set the calibration cache folder to some writable location on the PC
            XSCore90.XS_SetCalibrationFolder("e:\\CalCache");
            // Set this path to a folder on the computer. Be sure the path has write/create access
            // This holds the downloaded calibration file and speeds up subsequent XS_AutoConfig calls.

            // Use the following call with xTRUE if you are connecting to the sensors wirelessly - they must already be paired in Windows
            xbool bWirelessX4 = xbool.TRUE;
            XSCore90.XS_SetAllowX4Wireless(bWirelessX4); // wireless X4

            // Use the following call with xTRUE if you are connecting to the sensors over USB wire
            xbool bWiredX4 = xbool.TRUE;
            XSCore90.XS_SetAllowX4(bWiredX4);
            // If you use BOTH XS_SetAllowX4Wireless(xTRUE) and XS_SetAllowX4(xTRUE) at the same time, the DLL will favour USB wired over wireless.

            // Use 8 bit mode when transmitting over Bluetooth wireless to ensure higher framerates
            XSCore90.XS_SetX4Mode8Bit(bWirelessX4);
            XSCore90.XS_SetSampleAverageCount(4); // 4 or 8 for X4 sensors. 

            // we'll work in PSI for this demo
            EPressureUnit ePressureUnits = EPressureUnit.ePRESUNIT_PSI;

            // Automatically create a sensor configuration with all connected sensors using your preferred pressure units.
#if (true)
            if (XSCore90.XS_AutoConfig(ePressureUnits) != xbool.TRUE)
            {
                //printf("AutoConfig failed. Please check error codes.\nEXSErrorCodes=%s.\nEEnumerationError=%s\n", XSCore90.XS_GetLastErrorCodeAsString(), XSCore90.XS_GetLastEnumStateAsString());
                return;
            }
#else // or do the same but construct an XSN file that can be viewed in the XSENSOR desktop software.
	        if (XSCore90.XS_AutoConfigXSN("e:\\mySession.xsn", ePressureUnits) != xbool.TRUE)
	        {
		        //printf("AutoConfig failed. Please check error codes.\nEXSErrorCodes=%s.\nEEnumerationError=%s\n", XS_GetLastErrorCodeAsString(), XS_GetLastEnumStateAsString());
		        return;
	        }
#endif


            // query the configured sensors for their combined pressure range. (Different sensors may have different ranges.)
            float nMinPressure = 0.0f, nMaxPressure = 0.0f;
            XSCore90.XS_GetConfigInfo(ePressureUnits, ref nMinPressure, ref nMaxPressure);

            Console.WriteLine("Configured sensors are calibrated from " + nMinPressure.ToString() + " to " + nMaxPressure.ToString() + " " + ePressureUnits.ToString());


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

            // open a connection to the configured sensors
            if (XSCore90.XS_OpenConnection(75 * 60) == xbool.TRUE) // 75 Hz or 4500 frames per minute
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

                            // If the library was initialized with XS_InitLibrary(xTRUE),
                            // then XS_Sample will return immediately if there is a queued sample.
                        }
                        else
                        {
                            // If we're not running in a threaded mode, then XS_Sample blocks until a new sample is available.
                            nFrame++;

                            // If the library was initialized with XS_InitLibrary(xFALSE), 
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

                            if (XSCore90.XS_GetPressureSafe(spid, nCellCount, pressureMap) == xbool.TRUE)
                            {
                                // Fetch the pressure readings collected by the XS_Sample() call and place them in the buffer.
                                // Do this for each sensor in the configuration.
                                bool bDisplayNumbers = false;

                                if (bDisplayNumbers)
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
                                                Console.Write("0" + "\t");
                                                continue; // this is a dead sensel (typically for foot sensors this is a cell out side the sensing area)
                                            }

                                            cellCount++; // for averaging

                                            if (pressure > nMax)
                                                nMax = pressure;

                                            nAvg += pressure;

                                            Console.Write(pressure.ToString() + "\t");
                                        }
                                        Console.WriteLine("");
                                    }

                                    if (cellCount > 1)
                                        nAvg /= (float)cellCount;

                                    Console.WriteLine("AVG = " + nAvg.ToString() + "\tMAX = " + nMax.ToString());
                                }
                                else
                                {
                                    // display the data as an ASCII image
                                    ProcessFrame(pressureMap, nNbrRows, nNbrColumns, nMinPressure, nMaxPressure);
                                }
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
                Console.WriteLine("XS_OpenConnection failed. ERRORCODE=%" + XSCore90.XS_GetLastErrorCode().ToString());
            }
        } // end RunTest


        static void ProcessFrame(float[] pressureMap, ushort wRows, ushort wColumns, float nMinPressure, float nMaxPressure)
        {
            //    string isobarMapDarkToLight("@%#*+=-:. ");
            //            char isobarMapLightToDark[10] = " .:-=+*#%@";

            //isobarMapLightToDarkwchar_t isobarMapLightToDark[] = {' ','.',':','-','=','+','*','#','%','@' };
            string isobarMapLightToDark = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ";

            int nNbrIsobars = isobarMapLightToDark.Length;
            int nIsobar = 0;

            for (ushort wRow = 0; wRow < wRows; wRow++)
            {
                Console.Write("\t");
                for (ushort wColumn = 0; wColumn < wColumns; wColumn++)
                {
                    float pressure = pressureMap[wRow * wColumns + wColumn]; // use this calculations to traverse the array in a 2D manner

                    if (pressure < 0) // this means this cell is not in the grid (a dead sensel)
                        Console.Write(" ");

                    nIsobar = GetIsobar(pressure, nMinPressure, nMaxPressure, nNbrIsobars);
                    // convert the pressure to an ascii isobar
                    Console.Write(isobarMapLightToDark[nIsobar].ToString());

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
