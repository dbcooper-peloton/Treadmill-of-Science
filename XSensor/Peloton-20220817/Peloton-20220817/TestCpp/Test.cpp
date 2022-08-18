// TestCore70.cpp : Defines the entry point for the console application.
//


#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0601
#endif						

#ifndef _CRT_SECURE_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS
#endif

#include <windows.h>

#include <stdio.h>
#include <assert.h>

#include "../XSCore90.h"

#include "TestHelpers.hpp"

int RunTest();

int main()
{
	// Initialize the XS Core library
	XBOOL bThread = xTRUE;
	if (!XS_InitLibrary(bThread))
	{
		printf("XS_InitLibrary failed.  ERRORCODE=%ld\n", XS_GetLastErrorCode() );
		return 0;
	}

	uint16_t major, minor, build, revision;
	if (XS_GetVersion(major, minor, build, revision))
	{
		printf("DLL Version: %d.%d.%d.%d\n", major, minor, build, revision );
	}

	// RunTest - enumerate and configure all attached sensors for a selected pressure range, and take some samples
	RunTest();

	// deallocate resources and memory
	XS_ExitLibrary();

	return 0;
}


// ----------------------------------------------------------------------
//	RunTest
// 
//	Enumerate and configure all attached sensors and take some sample readings.
// ----------------------------------------------------------------------

int RunTest()
{
	// Set the calibration cache folder to some writable location on the PC
	XS_SetCalibrationFolderUTF8("e:\\CalCache");
	// Set this path to a folder on the computer. Be sure the path has write/create access
	// This holds the downloaded calibration file and speeds up subsequent XS_AutoConfig calls.

	// Use the following call with xTRUE if you are connecting to the sensors wirelessly - they must already be paired in Windows
	XBOOL bWirelessX4 = xTRUE;
	XS_SetAllowX4Wireless(bWirelessX4);

	// Use the following call with xTRUE if you are connecting to the sensors over USB wire
	XBOOL bWiredX4 = xTRUE;
	XS_SetAllowX4(bWiredX4);
	// If you use BOTH XS_SetAllowX4Wireless(xTRUE) and XS_SetAllowX4(xTRUE) at the same time, the DLL will favour USB wired over wireless.

	XS_SetX4Mode8Bit(bWirelessX4); // enable 8 bit for wireless X4 to ensure higher framerates
	XS_SetSampleAverageCount(4); // 4 or 8 for X4 sensors.

	XS_SetEnableIMU(xTRUE);

	// we'll work in PSI for this demo
	EPressureUnit ePressureUnits = ePRESUNIT_PSI;

	// Automatically create a sensor configuration with all connected sensors using your preferred pressure units.
#if(true)
	if (!XS_AutoConfig(ePressureUnits))
	{
		printf("AutoConfig failed. Please check error codes.\nEXSErrorCodes=%s.\nEEnumerationError=%s\n",
			XS_GetLastErrorCodeAsString(), XS_GetLastEnumStateAsString());
		return 0;
	}
#else // or do the same but construct an XSN file that can be viewed in the XSENSOR desktop software.
	if (!XS_AutoConfigXSN(L"e:\\mySession.xsn", ePressureUnits))
	{
		printf("AutoConfig failed. Please check error codes.\nEXSErrorCodes=%s.\nEEnumerationError=%s\n",
			XS_GetLastErrorCodeAsString(), XS_GetLastEnumStateAsString());
		return 0;
	}
#endif

	// query the configured sensors for their combined pressure range. (Different sensors may have different ranges.)
	float nMinPressure = 0.0f, nMaxPressure = 0.0f;
	XS_GetConfigInfo(ePressureUnits, nMinPressure, nMaxPressure);

	printf("Configured sensors are calibrated from %.03f to %.03f %s\n", nMinPressure, nMaxPressure, HELPER_GetPressureUnitLabel_ENG(ePressureUnits));

	// Fetch some details for each configured sensor
	uint32_t nNbrConfigured = XS_ConfigSensorCount();
	for (uint32_t nSensor = 0; nSensor < nNbrConfigured; nSensor++)
	{
		// fetch the sensor identifier
		SENSORPID spid = XS_ConfigSensorPID(nSensor);

		// fetch the sensor name
		char* pBuffer = nullptr;
		uint32_t bufferLength = 0; // number of wchar_t allocated

		// obtain the buffer size for the name
		if (XS_GetSensorNameUTF8(spid, bufferLength, nullptr) && (bufferLength > 0))
		{
			pBuffer = new char[bufferLength];

			if (pBuffer != nullptr)
			{
				if (XS_GetSensorNameUTF8(spid, bufferLength, pBuffer))
					printf("Sensor #%ld: %s S%04ld\n", nSensor + 1, pBuffer, XS_GetSerialFromPID(spid));

				delete[] pBuffer;
			}
		}


		// fetch the dimensions of a single cell
		float nSenselWidthCM = 0, nSenselHeightCM = 0;
		XS_GetSenselDims(spid, nSenselWidthCM, nSenselHeightCM);

		// Fetch the row and column counts for this sensor
		uint16_t rows, columns;
		XS_GetSensorDimensions(spid, rows, columns);

		printf("Width: %.02fcm  Height: %.02fcm\n", nSenselWidthCM * (float)columns, nSenselHeightCM * (float)rows);
	}


	// determine if a calibration file was set for all of the sensors.
	// Calibration files are stored on the sensors. These convert the raw electronic reading into a pressure reading.
	XBOOL bIsDataCalibrated = XS_IsCalibrationConfigured();

	if (!bIsDataCalibrated)
	{
		printf("Failed to download all calibration files. The sampled values are in RAW units only!\n");
	}

	// open a connection to the configured sensors
	if (XS_OpenConnection(75 * 60)) // 75 Hz or 4500 frames per minute
	{
		printf("XS_OpenConnection succeeded.\n");
		printf("XS_IsConnectionThreaded = %s\n", XS_IsConnectionThreaded() ? "yes" : "no");

		bool bThreaded = XS_IsConnectionThreaded() ? true : false;

		uint16_t year = 0;
		uint8_t month = 0, day = 0;
		uint8_t hour = 0, minute = 0, second = 0;
		uint16_t millisecond = 0;
		if (bThreaded)
			XS_GetSampleTimestampUTC(year, month, day, hour, minute, second, millisecond);

		uint8_t prevminute = minute;
		uint8_t prevsecond = second;
		uint16_t prevmillisecond = millisecond;
		uint16_t nNoSampleDelay = 0;

		// Attempt to collect a number of frames
		int nMaxFrames = 1; // just collecting one frame for this demonstration
		int nFrame = 0;

		while (nFrame < nMaxFrames)
		{
			// Tell the DLL to sample the configured sensors and generate a new frame
			if (XS_Sample())
			{
				if (bThreaded)
				{
					// If we're running in a threaded mode, then XS_Sample is an asynchronous call.
					// This means there may or may not be a new sample ready. In this case we must check
					// the timestamp of the current sample to see if it has changed.

					XS_GetSampleTimestampUTC(year, month, day, hour, minute, second, millisecond);
					assert(minute != 0);

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
						Sleep(10);
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
				for (uint32_t nSensor = 0; nSensor < nNbrConfigured; nSensor++)
				{
					SENSORPID spid = XS_ConfigSensorPID(nSensor);

					float qx, qy, qz, qw;
					float ax, ay, az;
					float gx, gy, gz;

					if (XS_GetIMU(spid, qx, qy, qz, qw, ax, ay, az, gx, gy, gz))
					{
						printf("IMU = {\n"
							"\tqx = %f\n"
							"\tqy = %f\n"
							"\tqz = %f\n"
							"\tqw = %f\n"
							"}\n", qx, qy, qz, qw);
					}


					// Fetching the dimensions of the sensor. These don't change, so this can be called outside the loop.
					uint16_t nNbrRows = 0, nNbrColumns = 0;
					XS_GetSensorDimensions(spid, nNbrRows, nNbrColumns);

					// compute the number of sensels in the sample
					uint32_t nCellCount = nNbrRows * nNbrColumns;
					if (nCellCount == 0)
						continue; // this should never occur

					// Allocate a buffer to hold the pressure.
					// Normally you would allocate this buffer only once and outside this loop!
					// You can allocate one buffer for each sensor, or one large buffer to hold all sensors.
					float* pPressure = new float[nCellCount];
					if (pPressure != nullptr)
					{
						// Fetch the pressure readings collected by the XS_Sample() call and place them in the buffer.
						// Do this for each sensor in the configuration.
						if (XS_GetPressure(spid, pPressure))
						{
							float nMax = 0.0f, nAvg = 0.0f;
							int cellCount = 0;

							bool bDisplayNumbers = true;

							// display the data as a set of numbers
							if (bDisplayNumbers)// display the pressure numbers
							{
								const float* pValue = pPressure;
								for (uint16_t nRow = 0; nRow < nNbrRows; nRow++)
								{
									for (uint16_t nColumn = 0; nColumn < nNbrColumns; nColumn++)
									{
										float pressure = *pValue++;

										if (pressure < 0)
										{
											//printf("%.03f\t", 0.0f);
											printf("-----\t");
											continue; // this is a dead sensel (typically for foot sensors this is a cell out side the sensing area)
										}

										cellCount++; // for averaging

										if (pressure > nMax)
											nMax = pressure;

										nAvg += pressure;

										printf("%.03f\t", pressure);
									}
									printf("\n");
								}

								if (cellCount > 1)
									nAvg /= (float)cellCount;

								printf("\nAVG = %f\tMAX = %f\n\n", nAvg, nMax);
							}
							else
							{
								// display the data as an ASCII image
								ProcessFrame(pPressure, nNbrRows, nNbrColumns, nMinPressure, nMaxPressure);
							}
						}

						delete[] pPressure;
					}
				}
			}
			else
			{
				// This is an odd condition. Perhaps the sensor became disconnected.
				printf("XS_Sample failed. ERRORCODE=%ld\n", XS_GetLastErrorCode());

				Sleep(10); // sleep 10 milliseconds, don't stave the CPU

				nNoSampleDelay += 10;
				if (nNoSampleDelay > 2000) // 2 seconds
					break; // too long of a delay between frames
			}
		} // next frame

		// Close all connections to the sensors.
		XS_CloseConnection();
	}
	else
	{
		printf("XS_OpenConnection failed. ERRORCODE=%ld\n", XS_GetLastErrorCode());
	}

	return 0;
}
