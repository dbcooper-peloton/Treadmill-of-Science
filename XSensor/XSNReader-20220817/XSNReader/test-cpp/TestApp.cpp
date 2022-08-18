// TestApp.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"

#include "../XSNReader.h"

// 32 bit lib - copy this somewhere on your library path
// Be sure to copy XSNReader.dll to the same location as the output exe!
#pragma comment(lib, "XSNReader.lib")


#include <stdio.h>
#include <assert.h>


bool RunTest1();
bool RunTest2();

int wmain(int argc, wchar_t* argv[])
{
	// Initialize the Core library
	if ( ! XSN_InitLibrary() )
	{
		wprintf(L"XSN_InitLibrary failed.  ERRORCODE=%ld\n", XSN_GetLastErrorCode() );
		return 0;
	}

	// basic test - not memory efficient - too many allocations/deallocations
	RunTest1();

	// basic test - more memory efficient - single memory allocation for the frame buffer
//	RunTest2();
	
	// deallocate resources and memory
	XSN_ExitLibrary();

	return 0;
}

// Helpers for demostration
int GetIsobar(float xpressure, float xminPressure, float xmaxPressure, int xbarCount)
{
	return (((xpressure) >= (xmaxPressure)) ? (int)((xbarCount)-1) : (((xpressure) < (xminPressure)) ? 0 : ((int)(((xpressure)-(xminPressure)) * ((xbarCount)-2) / ((xmaxPressure)-(xminPressure)) + 1))));
}

// Helpers for demostration
bool ProcessFrame(const float* pFrame, uint16_t wRows, uint16_t wColumns, float nMinPressure, float nMaxPressure)
{
	if (pFrame == nullptr)
		return false;

	//    wstring isobarMapDarkToLight(L"@%#*+=-:. ");
	//            char isobarMapLightToDark[10] = " .:-=+*#%@";

	//isobarMapLightToDarkwchar_t isobarMapLightToDark[] = {' ','.',':','-','=','+','*','#','%','@' };
	wchar_t isobarMapLightToDark[] = L"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ";

	// standard grey shade "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. "

	int nNbrIsobars = (int)(sizeof(isobarMapLightToDark) / sizeof(wchar_t));

	int nIsobar = 0;

	for (uint16_t wRow = 0; wRow < wRows; wRow++)
	{
		wprintf(L"\t");
		for (uint16_t wColumn = 0; wColumn < wColumns; wColumn++)
		{
			float pressure = pFrame[wRow * wColumns + wColumn]; // use this calculations to traverse the array in a 2D manner

			nIsobar = GetIsobar(pressure, nMinPressure, nMaxPressure, nNbrIsobars);
			// convert the pressure to an ascii isobar
			wprintf(L"%c", isobarMapLightToDark[nIsobar]);

		}

		wprintf(L"\n");
	}
	wprintf(L"\n");

	return true;

} // end ProcessFrame


// basic test - not memory efficient - too many allcations/deallocddations
bool RunTest1()
{
	// load the session
	//if (!XSN_LoadSessionU(L"E:\\xdata\\Sessions\\AutoSeat\\AutoSeatDemo27.xsn")) // unicode strings
	if ( ! XSN_LoadSession("demo.xsn") ) // utf8 strings
	{
		wprintf(L"XSN_LoadSessionU failed.  ERRORCODE=%ld\n", XSN_GetLastErrorCode() );
		return false;
	}

	// fetch information about the session
	wprintf(L"Session contains %ld frames\n", XSN_FrameCount() );
	wprintf(L"Session contains %ld pads\n", XSN_PadCount() );

	uint8_t nNbrPads = XSN_PadCount();
	for (uint8_t pad = 0; pad < nNbrPads; pad++ )
	{
		BSTR bsModel = nullptr;
		BSTR bsProductID = nullptr;
		BSTR bsSerial = nullptr;

		XSN_GetPadInfo(pad, &bsModel, &bsProductID, &bsSerial);

		float cellWidthCM = 0, cellHeightCM = 0;
		XSN_GetPadSenselDims(pad, cellWidthCM, cellHeightCM);

		wprintf(L"Pad%ld [%s %s %s] has %ld rows; %ld columns. Pad dims: %.02fcm width x %.02fcm length\n", 
			pad + 1, bsModel, bsProductID, bsSerial,XSN_Rows(pad), XSN_Columns(pad),
			cellWidthCM * (float)XSN_Columns(pad),
			cellHeightCM * (float)XSN_Rows(pad));

		SysFreeString(bsModel); // SysFreeString from oleauto.h
		SysFreeString(bsProductID);
		SysFreeString(bsSerial);
	}

	wprintf(L"Session base pressure units is %ld\n", XSN_GetPressureUnits() );

	XSN_SetPressureUnits(eXSNPRESUNIT_KGCM2);

	const wchar_t* szPressureUnits = L"kg/cm^2";
	const wchar_t* szAreaUnits = L"cm^2";

	EXSNForceUnit eForceUnits = XSN_GetForceUnits();
	const wchar_t* szForceLabels[] = { L"Unknown", L"N", L"kgf", L"lbf" };
	const wchar_t* szForceLabel = szForceLabels[0];

	if (eForceUnits == eXSNFORCEUNIT_NEWTONS)
		szForceLabel = szForceLabels[1];
	else if (eForceUnits == eXSNFORCEUNIT_KGF)
		szForceLabel = szForceLabels[2];
	else if (eForceUnits == eXSNFORCEUNIT_LBF)
		szForceLabel = szForceLabels[3];

	BSTR bsNotes;
	if (XSN_GetGeneralNotes(&bsNotes))
	{
		// treat bsNotes as wchar_t*, but be sure to SysFreeString() it!
		wprintf(L"General Notes: %s\n", bsNotes);
	}
	SysFreeString(bsNotes);



	uint32_t nNbrFrames = XSN_FrameCount();

	// for demo purposes, we'll limit output to a few frames

	if ( nNbrFrames > 3 )
		nNbrFrames = 3;


	uint16_t nYear, nMonth, nDay, nHour, nMinute, nSecond, nMilliseconds;

	// frame ID's are 1 based
	for (uint32_t nFrame = 1; nFrame <= nNbrFrames; nFrame++ )
	{
		// Step to the frame
		XSN_StepToFrame(nFrame);

		wprintf(L"Processing Frame ID %ld\n", XSN_GetFrameID() );

		if ( XSN_GetTimeStampUTC(nYear, nMonth, nDay, nHour, nMinute, nSecond, nMilliseconds) )
		{
			wprintf(L"Frame Timestamp: %04d-%02d-%02d  %02d:%02d:%02d.%04d\n", nYear, nMonth, nDay, nHour, nMinute, nSecond, nMilliseconds );
		}

		BSTR bsFrameNotes;
		if (XSN_GetFrameNotes(&bsFrameNotes))
		{
			// treat bsNotes as wchar_t*, but be sure to SysFreeString() it!
			wprintf(L"Frame Notes: %s\n", bsFrameNotes);
		}
		SysFreeString(bsFrameNotes);

		// pad indice are 0 based
		for (uint8_t pad = 0; pad < nNbrPads; pad++ )
		{
			float* pPressureMap = XSN_GetPressureMap(pad);

			if (pPressureMap != nullptr)
			{
				wprintf(L"Frame begins:\n");

				// STATISTICS
				float nZeroThreshold = 0.05f;// XSN_GetZeroThreshold(); // or replace this with your own threshold

				float nAvgPressure = XSN_GetStatAvgPressure(pad, nZeroThreshold);
				float nPeakPressure = XSN_GetStatPeakPressure(pad, nZeroThreshold);
				float nMinPressure = XSN_GetStatMinPressure(pad, nZeroThreshold);
				float nContactArea = XSN_GetStatContactAreaCM(pad, nZeroThreshold);
				float nEstLoad = XSN_GetStatEstimatedLoad(pad, nZeroThreshold);

				float column = 0, row = 0;

				XSN_GetCOP(pad, nZeroThreshold, column, row);

				wprintf(L"Frame Statistics\n");
				wprintf(L"\tAvg Pressure: %.02f %s\n", nAvgPressure, szPressureUnits);
				wprintf(L"\tMax Pressure: %.02f %s\n", nPeakPressure, szPressureUnits);
				wprintf(L"\tMin Pressure: %.02f %s\n", nMinPressure, szPressureUnits);
				wprintf(L"\tContact Area: %.02f %s\n", nContactArea, szAreaUnits);
				wprintf(L"\tEst. Load: %.02f %s\n", nEstLoad, szForceLabel);
				wprintf(L"\tCOP: row %.02f column %.02f\n", row, column);

				// PRESSURE MAP

				uint16_t nNbrRows = XSN_Rows(pad);
				uint16_t nNbrColumns = XSN_Columns(pad);

				ProcessFrame(pPressureMap, nNbrRows, nNbrColumns, XSN_GetMinPressure(), XSN_GetMaxPressure());

				wprintf(L"Frame Ends\n\n");

				XSN_FreePressureMap(pPressureMap);
			}
		}
	}

	// Close the session
	XSN_CloseSession();

	return true;
}

// basic test - more memory efficient
bool RunTest2()
{
	// load the session
	if ( ! XSN_LoadSessionU(L"demo.xsn") )
	{
		wprintf(L"XSN_LoadSessionU failed.  ERRORCODE=%ld\n", XSN_GetLastErrorCode() );
		return false;
	}

	// fetch information about the session
	wprintf(L"Session contains %ld frames\n", XSN_FrameCount() );
	wprintf(L"Session contains %ld pads\n", XSN_PadCount() );

	uint8_t nNbrPads = XSN_PadCount();
	for (uint8_t pad = 0; pad < nNbrPads; pad++)
	{
		BSTR bsModel = nullptr;
		BSTR bsProductID = nullptr;
		BSTR bsSerial = nullptr;

		XSN_GetPadInfo(pad, &bsModel, &bsProductID, &bsSerial);

		float cellWidthCM = 0, cellHeightCM = 0;
		XSN_GetPadSenselDims(pad, cellWidthCM, cellHeightCM);

		wprintf(L"Pad%ld [%s %s %s] has %ld rows; %ld columns. Pad dims: %.02fcm width x %.02fcm length\n",
			pad + 1, bsModel, bsProductID, bsSerial, XSN_Rows(pad), XSN_Columns(pad),
			cellWidthCM * (float)XSN_Columns(pad),
			cellHeightCM * (float)XSN_Rows(pad));

		SysFreeString(bsModel); // SysFreeString from oleauto.h
		SysFreeString(bsProductID);
		SysFreeString(bsSerial);
	}

	wprintf(L"Session base pressure units is %ld\n", XSN_GetPressureUnits() );

	uint32_t nNbrFrames = XSN_FrameCount();

	// for demo purposes, we'll limit output to a few frames

	if ( nNbrFrames > 3 )
		nNbrFrames = 3;

	uint16_t nYear, nMonth, nDay, nHour, nMinute, nSecond, nMilliseconds;

	// at most there can be 16 pads in a session
	float* arPressureMaps[16];
	
	// force a memory allocation for each pad
	for (uint8_t pad = 0; pad < nNbrPads; pad++ )
	{
		arPressureMaps[pad] = XSN_GetPressureMap(pad);

		assert( arPressureMaps[pad] != NULL );
	}

	// frame ID's are 1 based
	for (uint32_t nFrame = 1; nFrame <= nNbrFrames; nFrame++ )
	{
		XSN_StepToFrame(nFrame);

		wprintf(L"Processing Frame ID %ld\n", XSN_GetFrameID() );

		if ( XSN_GetTimeStampUTC(nYear, nMonth, nDay, nHour, nMinute, nSecond, nMilliseconds) )
		{
			wprintf(L"Frame Timestamp: %04d-%02d-%02d  %02d:%02d:%02d.%04d\n", nYear, nMonth, nDay, nHour, nMinute, nSecond, nMilliseconds );
		}


		// pad indice are 0 based
		for (uint8_t pad = 0; pad < nNbrPads; pad++ )
		{
			const float* pPressureMap = arPressureMaps[pad];

			XSN_CopyPressureMap(pad, arPressureMaps[pad]);

			if ( pPressureMap )
			{
				wprintf(L"Frame begins:\n");

				uint16_t nNbrRows = XSN_Rows(pad);
				uint16_t nNbrColumns = XSN_Columns(pad);

				for ( uint16_t nRow = 0; nRow < nNbrRows; nRow++ )
				{
					for ( uint16_t nColumn = 0; nColumn < nNbrColumns; nColumn++ )
					{
						float pressure = pPressureMap[nRow * nNbrColumns + nColumn];

						wprintf(L"%.03f; ", pressure );
					}

					wprintf(L"\n");
				}

				wprintf(L"Frame Ends\n");
			}
		}
	}

	// free pressure map memory
	for (uint8_t pad = 0; pad < nNbrPads; pad++ )
	{
		XSN_FreePressureMap(arPressureMaps[pad]);
	}


	// Close the session
	XSN_CloseSession();

	return true;
}
