"""
This Python script loads microphone data from a TDMS file, processes it, and saves it as a NumPy binary file (.npy).
The microphone data is extracted from the TDMS file, filtered using a Butterworth filter, and then zeroed out.
The processed data is saved to a .npy file for future use. If the processed data file already exists, it is loaded directly.

Summary of the program:
- Load microphone data from a TDMS file.
- Extract relevant information and timestamps.
- Convert TDMS file to MATLAB file format if necessary.
- Apply Butterworth filter to the microphone data.
- Zero out the filtered data.
- Save the processed data as a NumPy binary file.

Author: Daniel Cooper
Date: 3/13/2024
"""


import numpy as np
from datetime import datetime
from convertTDMS import convertTDMS  # Assuming this is a custom function
from scipy.signal import butter, lfilter


def load_MicData(fullfname_tdms):
    # Define file paths
    Dname, fname, _ = fullfname_tdms.rsplit('/', 2)
    fullfname_mat = f"{Dname}/{fname}.mat"

    # Load ForceData and extract relevant time information
    ForceData = load_ForceData(f"{Dname}/load_cells_Data.tdms")
    MicData = {'endTime': ForceData['endTime']}
    startTime = ForceData['footStrikeTime'][:, 0].flatten()[~np.isnan(ForceData['footStrikeTime'][:, 0])]
    startTime = startTime[~np.isnan(startTime)]

    # Assign mic start time vector to force start time vector
    MicData['startTimeSec'] = startTime

    # Check if MATLAB converted TDMS file exists, if not then convert TDMS into MATLAB file
    if not os.path.exists(fullfname_mat):
        Data = convertTDMS(0, fullfname_tdms)

        MicData['t'] = datetime.fromordinal(Data.Data.MeasuredData[3].Data.astype(int))
        MicData['t'] = MicData['t'].replace(tzinfo=None)
        MicData['t'] = MicData['t'].astimezone(timezone('America/Los_Angeles'))
        MicData['t'] = MicData['t'].strftime('%H:%M:%S.%f')

        G = 1 / (3.3 / 2)  # [unknown]
        Bias = 3.3 / 2
        MicData['Frnt_L'] = (Data.Data.MeasuredData[4].Data - Bias) * G
        MicData['Back_L'] = (Data.Data.MeasuredData[5].Data - Bias) * G
        MicData['Frnt_R'] = (Data.Data.MeasuredData[7].Data - Bias) * G
        MicData['Back_R'] = (Data.Data.MeasuredData[6].Data - Bias) * G
        MicData['sum'] = MicData['Frnt_L'] + MicData['Back_L'] + MicData['Frnt_R'] + MicData['Back_R']

        # Apply Butterworth Filter on sum of X
        fc = 50
        fs = 40000
        b, a = butter(6, fc / (fs / 2))
        MicData['Frnt_L_BW'] = lfilter(b, a, MicData['Frnt_L'])
        MicData['Back_L_BW'] = lfilter(b, a, MicData['Back_L'])
        MicData['Frnt_R_BW'] = lfilter(b, a, MicData['Frnt_R'])
        MicData['Back_R_BW'] = lfilter(b, a, MicData['Back_R'])

        # Zero out data
        FL_av = np.mean(MicData['Frnt_L_BW'][:40000])
        BL_av = np.mean(MicData['Back_L_BW'][:40000])
        FR_av = np.mean(MicData['Frnt_R_BW'][:40000])
        BR_av = np.mean(MicData['Back_R_BW'][:40000])
        FL_zero = MicData['Frnt_L_BW'] - FL_av
        BL_zero = MicData['Back_L_BW'] - BL_av
        FR_zero = MicData['Frnt_R_BW'] - FR_av
        BR_zero = MicData['Back_R_BW'] - BR_av

        MicData['accelTime'] = MicData['t']
        MicData['footStrikeFL'] = np.zeros((1, 100000))
        MicData['footStrikeBL'] = np.zeros((1, 100000))
        MicData['footStrikeFR'] = np.zeros((1, 100000))
        MicData['footStrikeBR'] = np.zeros((1, 100000))
        MicData['footStrikeSum'] = np.zeros((1, 100000))
        MicData['footStrikeTime'] = np.full((1, 100000), np.datetime64('NaT'))

        j = 0
        for i, accelTime in enumerate(MicData['accelTime']):
            if MicData['startTimeSec'][j] <= accelTime:
                if accelTime <= MicData['endTime'][j]:
                    MicData['footStrikeFL'][j, i] = FL_zero[i]
                    MicData['footStrikeBL'][j, i] = BL_zero[i]
                    MicData['footStrikeFR'][j, i] = FR_zero[i]
                    MicData['footStrikeBR'][j, i] = BR_zero[i]
                    MicData['footStrikeSum'][j, i] = MicData['sum'][i]
                    MicData['footStrikeTime'][j, i] = accelTime
                else:
                    MicData['footStrikeFL'][j, i] = -1
                    MicData['footStrikeBL'][j, i] = -1
                    MicData['footStrikeFR'][j, i] = -1
                    MicData['footStrikeBR'][j, i] = -1
                    MicData['footStrikeSum'][j, i] = -1
                    MicData['footStrikeTime'][j, i] = np.datetime64('NaT')
                    j += 1
                    if j == len(MicData['endTime']):
                        break

        np.save(fullfname_mat, MicData)
    else:
        MicData = np.load(fullfname_mat, allow_pickle=True).item()

    return MicData
