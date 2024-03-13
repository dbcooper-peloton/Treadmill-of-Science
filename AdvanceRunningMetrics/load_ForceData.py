"""
This Python function loads force data from a TDMS file, processes it, and saves it as a NumPy binary file (.npy).
The force data is extracted from the TDMS file, filtered using a Butterworth filter, and then processed.
The processed data is saved to a .npy file for future use. If the processed data file already exists, it is loaded directly.

Summary of the program:
- Load force data from a TDMS file.
- Extract relevant information and timestamps.
- Convert TDMS file to MATLAB file format if necessary.
- Apply Butterworth filter to the force data.
- Zero out the filtered data.
- Sum the forces and calculate force zones.
- Implement a snapshot algorithm to create two-second snapshots of force data.
- Save the processed data as a NumPy binary file.

Author: Daniel Cooper
Date: 3/13/2024
"""

import os
from nptdms import TdmsFile
import numpy as np
from scipy.signal import butter, filtfilt


def load_ForceData(fullfname_tdms):
    # Define file paths
    dirname, fname = os.path.split(fullfname_tdms)
    fname, _ = os.path.splitext(fname)
    fullfname_mat = os.path.join(dirname, fname + '.mat')

    if not os.path.exists(fullfname_mat):
        # Load TDMS file
        tdms_file = TdmsFile.read(fullfname_tdms)

        # Extract data
        measured_data = tdms_file['MeasuredData']

        ForceData = {}
        ForceData['t'] = measured_data['t'].time_track()
        ForceData['t'] = ForceData['t'].astype('datetime64[s]')

        # Convert from volts to pounds-force
        G = 1 / 0.02

        # Extract force data for each channel and convert units
        channels = ['Frnt_L', 'FMid_L', 'BMid_L', 'Back_L',
                    'Frnt_R', 'FMid_R', 'BMid_R', 'Back_R']
        for i, channel in enumerate(channels):
            ForceData[channel] = measured_data[i].data * G

        # Butterworth filter parameters
        fc = 30  # Cutoff frequency
        fs = 2000  # Sampling frequency
        order = 6

        # Apply Butterworth filter to each force data
        b, a = butter(order, fc / (fs / 2))
        filtered_data = {key: filtfilt(b, a, value) for key, value in ForceData.items() if
                         isinstance(value, np.ndarray)}

        # Compute mean of first 2 seconds
        window_size = 2000
        for key, value in filtered_data.items():
            ForceData[key + '_av'] = np.mean(value[:window_size])

        # Zero out forces by subtracting mean
        for key, value in filtered_data.items():
            ForceData[key + '_zero'] = value - ForceData[key + '_av']

        # Sum of forces after zeroing
        ForceData['sum'] = np.sum([ForceData[key + '_zero'] for key in channels], axis=0)

        # Zone-wise sums
        ForceData['zone1'] = ForceData['Frnt_L_zero'] + ForceData['Frnt_R_zero']
        ForceData['zone2'] = ForceData['FMid_L_zero'] + ForceData['FMid_R_zero']
        ForceData['zone3'] = ForceData['BMid_L_zero'] + ForceData['BMid_R_zero']
        ForceData['zone4'] = ForceData['Back_L_zero'] + ForceData['Back_R_zero']
        ForceData['LEFT'] = ForceData['Frnt_L_zero'] + ForceData['FMid_L_zero'] + ForceData['BMid_L_zero'] + ForceData[
            'Back_L_zero']
        ForceData['RIGHT'] = ForceData['Frnt_R_zero'] + ForceData['FMid_R_zero'] + ForceData['BMid_R_zero'] + ForceData[
            'Back_R_zero']

        # Snapshot algorithm
        threshold = 30
        snapshot_data = []
        for i, force_sum in enumerate(ForceData['sum']):
            if force_sum > threshold:
                snapshot_data.append({key: value[i] for key, value in filtered_data.items()})
            elif len(snapshot_data) > 0:
                if len(snapshot_data[-1]) < 20 or len(snapshot_data[-1]) > 4000:
                    snapshot_data.pop()

        # Convert snapshot data to matrices
        snapshot_matrices = {key: np.vstack([snapshot[key] for snapshot in snapshot_data]) for key in
                             filtered_data.keys()}

        # Add snapshot matrices to ForceData
        ForceData.update(snapshot_matrices)

        # Save to .mat file
        np.savez(fullfname_mat, **ForceData)
    else:
        # Load existing .mat file
        ForceData = np.load(fullfname_mat, allow_pickle=True)
        ForceData = ForceData.item()

    return ForceData
