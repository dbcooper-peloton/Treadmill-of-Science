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

#include <vector> // C++ STL library

#include "../XSCore90.h"

#include "TestHelpers.hpp"

// Enumerate and configure all attached sensors and take some sample readings.
void RunLocalSession(bool allowX4, bool wirelessX4=false);

//	Enumerate and configure the first found insole sensor and start or 
//  stop a remote session.
void RunRemoteSessionSingle(bool wirelessX4);

// works with a left/right insole pair
void RunRemoteSessionPair(bool wirelessX4);

int main()
{
	// Initialize the XS Core library
	XBOOL bThread = xTRUE; // X3 should be polled
	if (!XS_InitLibrary(bThread))
	{
		printf("XS_InitLibrary failed.  ERRORCODE=%s\n", XS_GetLastEnumStateAsString());
		return 0;
	}
	

	uint16_t major = 0, minor = 0, build = 0, revision = 0;
	XS_GetVersion(major, minor, build, revision);

	printf("DLL Version: %d.%d.%d.%d\n", major, minor, build, revision );

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
		//RunRemoteSessionSingle(false);

		//	Enumerate and configure the first left/right insole sensors and start or 
		//  stop a remote session.
		RunRemoteSessionPair(false);
	}

	// deallocate resources and memory
	XS_ExitLibrary();

	return 0;
}


// ----------------------------------------------------------------------
//	RunLocalSession
// 
//	Enumerate and configure all attached sensors and take some sample readings.
// ----------------------------------------------------------------------

void RunLocalSession(bool allowX4, bool wirelessX4)
{
	printf("Running local session test\n");
	printf("Setting calibration cache...\n");

	// Set the calibration cache folder to some writable location on the PC
	XS_SetCalibrationFolderUTF8("e:\\CalCache");
	// Set this path to a folder on the computer. Be sure the path has write/create access
	// This holds the downloaded calibration file and speeds up subsequent XS_AutoConfig calls.

	uint32_t framesPerMinute = 10 * 60; // 10 Hz

	bool enableIMU = false;

	if (allowX4)
	{
		XS_SetAllowX4Wireless(wirelessX4 ? xTRUE : xFALSE);

		// Use the following call with xTRUE if you are connecting to the sensors over USB wire
		XS_SetAllowX4((!wirelessX4) ? xTRUE : xFALSE);
		// If you use BOTH XS_SetAllowX4Wireless(xTRUE) and XS_SetAllowX4(xTRUE) at the same time, the DLL will favour USB wired over wireless.

		// Use 8 bit mode when transmitting over Bluetooth wireless to ensure higher framerates
		XS_SetX4Mode8Bit(wirelessX4 ? xTRUE : xFALSE);
		XS_SetSampleAverageCount(4); // 4 or 8 for X4 sensors. smaller number is faster, but with slightly worse signal-to-noise

		framesPerMinute = 75 * 60; // 75 Hz

		// if you're testing X4 insole sensor, you can use this
		if (enableIMU)
			XS_SetEnableIMU(xTRUE); // if we want IMU data with each frame

		// note: if an X3 sensor is attached it will also be enumerated
	}
	// else - by default X4 is off ... so only X3 sensors will be picked up
	else
	{
		enableIMU = false; // not supported by X3

		// 1, 2, 4, 8 for X3 sensors. smaller number is faster, but with slightly worse signal-to-noise
		XS_SetSampleAverageCount(1);
	}


	// we'll work in PSI for this demo
	EPressureUnit ePressureUnits = ePRESUNIT_PSI;
	XS_SetPressureUnit(ePressureUnits);


	printf("Enumerating sensors and configuring...\n");
#if(true)
	// Automatically create a sensor configuration with all connected sensors using your preferred pressure units.
	if (!XS_AutoConfig(ePressureUnits))
	{
		printf("AutoConfig failed. Please check error codes.\nEXSErrorCodes=%s.\nEEnumerationError=%s\n",
			XS_GetLastErrorCodeAsString(), XS_GetLastEnumStateAsString());
		return;
	}
#else // or do the same but construct an XSN file that can be viewed in the XSENSOR desktop software.
	if (!XS_AutoConfigXSN(L"e:\\mySession.xsn", ePressureUnits))
	{
		printf("AutoConfig failed. Please check error codes.\nEXSErrorCodes=%s.\nEEnumerationError=%s\n",
			XS_GetLastErrorCodeAsString(), XS_GetLastEnumStateAsString());
		return;
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

	printf("Opening connection to sensors...\n");

	// open a connection to the configured sensors
	if (XS_OpenConnection(framesPerMinute))
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

					XS_GetSampleTimestampUTC(year, month, day, hour, minute, second, millisecond);

					// If the library was initialized with XS_InitLibrary(xFALSE), 
					// then XS_Sample will block until a sample is collected - or it will timeout
				}


				// Retrieve the pressure data from the DLL's buffers

				// retrieve the data for each sensor
				for (uint32_t nSensor = 0; nSensor < nNbrConfigured; nSensor++)
				{
					SENSORPID spid = XS_ConfigSensorPID(nSensor);

					// Fetching the dimensions of the sensor. These don't change, so this can be called outside the loop.
					uint16_t nNbrRows = 0, nNbrColumns = 0;
					XS_GetSensorDimensions(spid, nNbrRows, nNbrColumns);

					// compute the number of sensels in the sample
					int nCellCount = nNbrRows * nNbrColumns;
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
							if (enableIMU)
							{
								float qx = 0, qy = 0, qz = 0, qw = 0;
								float ax = 0, ay = 0, az = 0;
								float gx = 0, gy = 0, gz = 0;

								// IMU data is refreshed with each new frame from the insole sensor
								if (XS_GetIMU(spid, qx, qy, qz, qw, ax, ay, az, gx, gy, gz))
								{
									printf("IMU = {\n"
										"\tqx = %f\n"
										"\tqy = %f\n"
										"\tqz = %f\n"
										"\tqw = %f\n"
										"}\n", qx, qy, qz, qw);
								}
							}

							bool bDisplayNumbers = true;
							DumpFrame(pPressure, nNbrColumns, nNbrRows, bDisplayNumbers, nMinPressure, nMaxPressure);
						}

						delete[] pPressure;
					}
				}
			}
			else
			{
				// This is an odd condition. Perhaps the sensor became disconnected.
				printf("XS_Sample failed. ERRORCODE=%s\n", XS_GetLastEnumStateAsString());

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
		printf("XS_OpenConnection failed. ERRORCODE=%s\n", XS_GetLastEnumStateAsString());
	}
}

// ----------------------------------------------------------------------
//	RunRemoteSessionSingle
// 
//	Enumerate and configure the first found insole sensor and start or 
//  stop a remote session.
// ----------------------------------------------------------------------

void RunRemoteSessionSingle(bool wirelessX4)
{
	printf("Running remote session single insole test\n");
	printf("Setting calibration cache...\n");

	// Set the calibration cache folder to some writable location on the PC
	// This folder is also used for tracking X4 state (x4tokens.bin)
	XS_SetCalibrationFolderUTF8("e:\\CalCache");
	// Set this path to a folder on the computer. Be sure the path has write/create access
	// This holds the downloaded calibration file and speeds up subsequent XS_AutoConfig calls.

	// Use the following call with xTRUE if you are connecting to the sensors wirelessly - they must already be paired in Windows
	XS_SetAllowX4Wireless(wirelessX4 ? xTRUE : xFALSE);

	// Use the following call with xTRUE if you are connecting to the sensors over USB wire
	XS_SetAllowX4(!wirelessX4 ? xTRUE : xFALSE);
	// If you use BOTH XS_SetAllowX4Wireless(xTRUE) and XS_SetAllowX4(xTRUE) at the same time, the DLL will favour USB wired over wireless.

	XS_SetX4Mode8Bit(wirelessX4 ? xTRUE : xFALSE); // enable 8 bit for wireless X4 to ensure higher framerates
	XS_SetSampleAverageCount(4); // 4 or 8 for X4 sensors.

	XS_SetEnableIMU(xFALSE);

	XS_SetPressureUnit(ePRESUNIT_PSI);

	// Be care with XS_EnumSensors as it will interrupt any will not discovery any new X4's if they're in the middle of a remote recording!

	// Normally enumeration will disrupt X4 remote recordings. We'll turn that off here.
	XS_SetAllowEnumInterruptX4Remote(xFALSE);

	// scan for available sensors - can take a while as it tries all known connections
	uint32_t sensorCount = XS_EnumSensors();
	if (sensorCount == 0)
	{
		printf("No available sensors found for remote test.\n");
		return;
	}

	bool bFound = false;
	SENSORPID spid = 0ull;
	XBOOL bFootSensor = xFALSE;
	XBOOL bLeftFoot = xFALSE;

	// we'll connect to the first X4 we find
	for (uint32_t sensor = 0; sensor < sensorCount; sensor++)
	{
		spid = XS_EnumSensorPID(sensor);

		if (XS_IsX4FootSensor(spid, bFootSensor, bLeftFoot) && bFootSensor)
		{
			bFound = true;

			uint32_t bufferSize = 0;
			XS_GetSensorNameUTF8(spid, bufferSize);

		#if(0) // just using C code
			char* nameBuffer = new char[bufferSize];
			XS_GetSensorNameUTF8(spid, bufferSize, nameBuffer);
			printf("Found X4 foot sensor [%s]\n", nameBuffer);
			delete[] nameBuffer;
		#else // using C++ code and libraries for memory management
			std::vector<char> nameBuffer;
			nameBuffer.resize(bufferSize); // note this includes a null terminator
			XS_GetSensorNameUTF8(spid, bufferSize, nameBuffer.data());
			printf("Found X4 foot sensor [%s]\n", nameBuffer.data());
		#endif

			break;
		}
	}

	if (!bFound)
	{
		printf("No X4 foot sensors found with active SD cards\n");
		return;
	}

	// Open a connection to the X4
	if (!X4_OpenRemote(spid))
	{
		printf("X4 remote command failed with error [%s]\n", XS_GetLastErrorCodeAsString());
		return;
	}

	// check if a recording is in progress
	XBOOL remoteRecording = xFALSE;
	if (X4_IsRemoteRecording(spid, &remoteRecording))
	{
		printf("X4 remote recording session is %s\n", remoteRecording ? "active" : "not active");

		if (remoteRecording)
		{
			printf("Stopping X4 remote recording\n");
			X4_StopRemoteRecording(spid);

			// now close the connection
			X4_CloseRemote(spid);
			return;
		}
	}
	else
	{
		printf("X4 remote command failed with error [%s]\n", XS_GetLastErrorCodeAsString());
	}


	printf("Prepping for X4 remote recording\n");

	float frameRateHz = 40.0f;
	if (X4_StartRemoteRecording(spid, frameRateHz))
	{
		printf("X4 remote recording started\n");

		Sleep(100); // give it some time to generate some frames

		printf("Fetching preview frame\n");
		if (X4_SampleRemote(spid))
		{
			// Fetching the dimensions of the sensor. These don't change, so this can be called outside the loop.
			uint16_t nNbrRows = 0, nNbrColumns = 0;
			XS_GetSensorDimensions(spid, nNbrRows, nNbrColumns);

			// compute the number of sensels in the sample
			int nCellCount = nNbrRows * nNbrColumns;

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
					bool bDisplayNumbers = true;

					float nMinPressure = 0;
					float nMaxPressure = 200.0f;
					X4_GetRemoteSampleRange(spid, XS_GetPressureUnit(), &nMinPressure, &nMaxPressure);

					DumpFrame(pPressure, nNbrColumns, nNbrRows, bDisplayNumbers, nMinPressure, nMaxPressure);
				}

				delete[] pPressure;
			}
		}
	}
	else
	{
		printf("X4 remote command failed with error [%s]\n", XS_GetLastErrorCodeAsString());
	}

	// close the connection
	X4_CloseRemote(spid);
}

// ----------------------------------------------------------------------
//	RunRemoteSessionPair
// 
//	Enumerate and configure the first left/right insole sensors and start or 
//  stop a remote session.
// ----------------------------------------------------------------------
void RunRemoteSessionPair(bool wirelessX4)
{
	printf("Running remote session insole pair test\n");
	printf("Setting calibration cache...\n");

	// Set the calibration cache folder to some writable location on the PC
	// This folder is also used for tracking X4 state (x4tokens.bin)
	XS_SetCalibrationFolderUTF8("e:\\CalCache");
	// Set this path to a folder on the computer. Be sure the path has write/create access
	// This holds the downloaded calibration file and speeds up subsequent XS_AutoConfig calls.

	// Use the following call with xTRUE if you are connecting to the sensors wirelessly - they must already be paired in Windows
	XS_SetAllowX4Wireless(wirelessX4 ? xTRUE : xFALSE);

	// Use the following call with xTRUE if you are connecting to the sensors over USB wire
	XS_SetAllowX4(!wirelessX4 ? xTRUE : xFALSE);
	// If you use BOTH XS_SetAllowX4Wireless(xTRUE) and XS_SetAllowX4(xTRUE) at the same time, the DLL will favour USB wired over wireless.

	XS_SetX4Mode8Bit(wirelessX4 ? xTRUE : xFALSE); // enable 8 bit for wireless X4 to ensure higher framerates
	XS_SetSampleAverageCount(4); // 4 or 8 for X4 sensors.

	XS_SetEnableIMU(xFALSE);

	XS_SetPressureUnit(ePRESUNIT_PSI);

	// Be care with XS_EnumSensors as it will interrupt any will not discovery any new X4's if they're in the middle of a remote recording!

	// Normally enumeration will disrupt X4 remote recordings. We'll turn that off here.
	XS_SetAllowEnumInterruptX4Remote(xTRUE);

	// scan for available sensors - can take a while as it tries all known connections
	uint32_t sensorCount = XS_EnumSensors();
	if (sensorCount == 0)
	{
		printf("No available sensors found for remote test.\n");
		return;
	}


	SENSORPID spid = 0ull;	// sensor pad id
	SENSORPID spidLeft = 0ull;
	SENSORPID spidRight = 0ull;
	XBOOL bFootSensor = xFALSE;
	XBOOL bLeftFoot = xFALSE;

	// we'll connect to the first X4 we find
	for (uint32_t sensor = 0; sensor < sensorCount; sensor++)
	{
		spid = XS_EnumSensorPID(sensor);

		if (XS_IsX4FootSensor(spid, bFootSensor, bLeftFoot) && bFootSensor)
		{
			uint32_t bufferSize = 0;
			XS_GetSensorNameUTF8(spid, bufferSize);

		#if(0) // just using C code
			char* nameBuffer = new char[bufferSize];
			XS_GetSensorNameUTF8(spid, bufferSize, nameBuffer);
			printf("Found X4 foot sensor [%s]\n", nameBuffer);
			delete[] nameBuffer;
		#else // using C++ code and libraries for memory management
			std::vector<char> nameBuffer;
			nameBuffer.resize(bufferSize); // note this includes a null terminator
			XS_GetSensorNameUTF8(spid, bufferSize, nameBuffer.data());
			printf("Found X4 foot sensor [%s]\n", nameBuffer.data());
		#endif
			// alter

			if (bLeftFoot)
			{
				if (spidLeft == 0ull)
					spidLeft = spid;
			}
			else //if (!bLeftFoot)
			{
				if (spidRight == 0ull)
					spidRight = spid;
			}
		}
	}


	if ((spidLeft == 0ull) || (spidRight == 0ull))
	{
		printf("No X4 pair of insole sensors found.\n");
		return;
	}

	// we have a pair!
	// Open a connection to the X4
	if (!X4_OpenRemote(spidLeft))
	{
		printf("Could not open a connection to the left insole: error [%s]\n", XS_GetLastErrorCodeAsString());
		return;
	}
	if (!X4_OpenRemote(spidRight))
	{
		X4_CloseRemote(spidLeft);
		printf("Could not open a connection to the right insole: error [%s]\n", XS_GetLastErrorCodeAsString());
		return;
	}


	// check if a recording is in progress
	XBOOL remoteRecordingLeft = xFALSE;
	XBOOL remoteRecordingRight = xFALSE;

	if(!X4_IsRemoteRecording(spidLeft, &remoteRecordingLeft))
		printf("X4 remote command failed with error [%s]\n", XS_GetLastErrorCodeAsString());

	if(!X4_IsRemoteRecording(spidRight, &remoteRecordingRight))
		printf("X4 remote command failed with error [%s]\n", XS_GetLastErrorCodeAsString());

	printf("X4 (left insole) remote recording session is %s\n", remoteRecordingLeft ? "active" : "not active");
	printf("X4 (right insole) remote recording session is %s\n", remoteRecordingRight ? "active" : "not active");

	if (remoteRecordingLeft && !remoteRecordingRight)
	{
		printf("Stopping left X4 remote recording\n");
		X4_StopRemoteRecording(spidLeft);
		X4_CloseRemote(spidLeft);
		X4_CloseRemote(spidRight);
		return;
	}
	else if (!remoteRecordingLeft && remoteRecordingRight)
	{
		printf("Stopping right X4 remote recording\n");
		X4_StopRemoteRecording(spidRight);
		X4_CloseRemote(spidLeft);
		X4_CloseRemote(spidRight);
		return;
	}

	// both are recording
	if (remoteRecordingLeft && remoteRecordingRight)
	{
		printf("Stopping X4 remote recording\n");
		X4_StopRemotePairRecording(spidLeft, spidRight);

		// now close the connection
		X4_CloseRemote(spidLeft);
		X4_CloseRemote(spidRight);
		return;
	}


	// attempt session download and conversion
	uint32_t minutes = 0;
	float frameRateHz = 40.0f;

	if (X4_GetRemoteDuration(spidLeft, frameRateHz, &minutes))
		printf("X4 left insole has %ld minutes available @ %.01f Hz for recording.\n", minutes, frameRateHz);

	if (X4_GetRemoteDuration(spidRight, frameRateHz, &minutes))
		printf("X4 right insole has %ld minutes available @ %.01f Hz for recording.\n", minutes, frameRateHz);

	printf("Prepping for X4 remote paired recording\n");
	if (X4_StartRemotePairRecording(spidLeft, spidRight, frameRateHz))
	{
		printf("X4 remote paired recording started\n");
	}
	else
	{
		printf("X4 remote paired command failed with error [%s]\n", XS_GetLastErrorCodeAsString());
	}

	// close the connections
	X4_CloseRemote(spidLeft);
	X4_CloseRemote(spidRight);
}
