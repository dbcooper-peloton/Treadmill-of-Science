
#include <stdint.h>


// this code shows how the center of pressure is calculated in XS_CenterOfPressure
bool ComputeCOP(
	const float* pSensels, uint16_t nNbrColumns, uint16_t nNbrRows, float nPressureThreshold,
	float& nCOPColumnNormal, float& nCOPRowNormal, uint16_t& nCOPColumn, uint16_t& nCOPRow)
{

	if (pSensels == nullptr)
	{
		nCOPColumn = nNbrColumns / 2;
		nCOPRow = nNbrRows / 2;

		nCOPColumnNormal = 0.5f;
		nCOPRowNormal = 0.5f;
		return false;
	}

	// ------------------------------------------------------------------
	// ------------------------------------------------------------------
	//			COMPUTE THE CENTER OF GRAVITY - TARGETED PAD & SUB-RECT
	// ------------------------------------------------------------------
	// ------------------------------------------------------------------
	bool bValidCOP = false; // invalid ratio if no pressure

	// https://en.wikipedia.org/wiki/Center_of_mass#Center_of_gravity
	// A system of particles

	// Let R be the vector coordinates of the center of mass
	// Let M be the sum of all pressure
	// let r[i] be the vector coordinate of each sensel
	// let m[i] be the pressure of each sensel
	//
	// R = 1/M x SUM( m[i] x r[i] ) where i = 1 to #sensels


	float pressure = 0;

	double nPressureTotal = 0;
	double nRowCoorAccum = 0;
	double nColCoorAccum = 0;

	for (uint16_t nRow = 0; nRow < nNbrRows; nRow++)
	{
		for (uint16_t nColumn = 0; nColumn < nNbrColumns; nColumn++)
		{
			pressure = pSensels[nRow * nNbrColumns + nColumn];

			if (pressure >= nPressureThreshold)
			{
				nPressureTotal += (double)pressure;
				nColCoorAccum += (double)((nColumn + 1) * pressure); // SUM( m[i] x r[i].x )
				nRowCoorAccum += (double)((nRow + 1) * pressure); // SUM( m[i] x r[i].y )
			}
		}
	}

	if (nPressureTotal > 0.0)
	{
		bValidCOP = true;

		nCOPColumn = (uint16_t)(nColCoorAccum / nPressureTotal - 1.0);
		nCOPRow = (uint16_t)(nRowCoorAccum / nPressureTotal - 1.0f);

		nCOPColumnNormal = (float)((((nColCoorAccum) / nPressureTotal) - 0.5) / ((double)nNbrColumns));
		nCOPRowNormal = (float)((((nRowCoorAccum) / nPressureTotal) - 0.5) / ((double)nNbrRows));
	}
	else
	{
		nCOPColumn = nNbrColumns / 2;
		nCOPRow = nNbrRows / 2;

		nCOPColumnNormal = 0.5f;
		nCOPRowNormal = 0.5f;

		bValidCOP = false;
	}

	return bValidCOP;
}


int GetIsobar(float xpressure, float xminPressure, float xmaxPressure, int xbarCount)
{
	return (((xpressure) >= (xmaxPressure)) ? (int)((xbarCount)-1) : (((xpressure) < (xminPressure)) ? 0 : ((int)(((xpressure)-(xminPressure)) * ((xbarCount)-2) / ((xmaxPressure)-(xminPressure)) + 1))));
}


void ProcessFrame(const float* pFrame, uint16_t wRows, uint16_t wColumns, float nMinPressure, float nMaxPressure)
{
	if (pFrame == nullptr)
		return;

	const char* isobarMapLightToDark = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ";

	int nNbrIsobars = (int)strlen(isobarMapLightToDark);
	int nIsobar = 0;

	for (uint16_t wRow = 0; wRow < wRows; wRow++)
	{
		printf("\t");
		for (uint16_t wColumn = 0; wColumn < wColumns; wColumn++)
		{
			float pressure = (float)pFrame[wRow * wColumns + wColumn]; // use this calculations to traverse the array in a 2D manner

			if(pressure < 0) // this means this cell is not in the grid (a dead sensel)
				printf(" ");

			nIsobar = GetIsobar(pressure, nMinPressure, nMaxPressure, nNbrIsobars);
			// convert the pressure to an ascii isobar
			printf("%c", isobarMapLightToDark[nIsobar]);

		}

		printf("\n");
	}
	printf("\n");

} // end ProcessFrame

const char* HELPER_GetPressureUnitLabel_ENG(EPressureUnit ePressureUnits)
{
	switch (ePressureUnits)
	{
	case ePRESUNIT_MMHG:	// millimeters of mercury
		return "mmHg";
	case ePRESUNIT_INH2O:	// inches of water
		return "inH2O";
	case ePRESUNIT_PSI:		// pounds/sq.inch
		return "PSI";
	case ePRESUNIT_KPA:		// kilopascals
		return "kpa";
	case ePRESUNIT_KGCM2:	// kgf/cm^2
		return "kgf/cm^2";
	case ePRESUNIT_ATM:		// atmospheres
		return "atm";
	case ePRESUNIT_NCM2:		// newtons/cm^2
		return "N/cm^2";
	case ePRESUNIT_MBAR:		// millibars
		return "mbar";
	case ePRESUNIT_NM2:		// Newton/meter^2
		return "N/m^2";
	case ePRESUNIT_GCM2:		// grams/cm^2
		return "g/m^2";
	case ePRESUNIT_BAR:		// bar
		return "bar";
	case ePRESUNIT_RAW:
		return "raw";
	default:
		break;
	}

	return "unknown - programming error";
}