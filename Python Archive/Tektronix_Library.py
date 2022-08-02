import pandas as pd
import numpy as np
from pyvisa import ResourceManager
from datetime import datetime

class DPO2024B:
    def __init__(self, Tek_dev):
        self.rm = ResourceManager()
        self.osc1 = self.rm.open_resource(Tek_dev)

        # Time and Date Connected
        self.curr_time = datetime.now()
        print(self.curr_time.strftime('%Y-%m-%d %H:%M:%S') + " Oscilloscope Connected")

    '''
    Retrieve Connected Oscilloscope ID
    '''

    def oscilloscope_ID(self):
        print(self.osc1.query('*IDN?'))

    '''
    Take Displayed Waveform from Oscilloscope as Data Points:
    1. Retrieve Raw Curve Data from Oscilloscope in Real Time
    2. Set the Curve to a scale from 0 to 1
    3. Scale the Curve to Actual Curve amplitude
    4. Offset the Curve to Actual Curve Min
    '''

    def waveform_RAW(self, CH_num):
        # Set Input Requirement
        self.osc1.write('DATA:SOURCE CH' + str(CH_num))      #Select CH
        self.osc1.write('DATA:RESOLUTION FULL')              #Set Data Resolution
        self.osc1.write('DATA:COMPOSITION COMPOSITE_YT')
        self.osc1.write('DATA:ENCDG SRPbinary')              #Set Data Encoding
        self.osc1.write('DATA:START 1')
        self.osc1.write('DATA:STOP 125000')

        # Acquire Waveform (RAW) From Oscilloscope
        buffer = self.osc1.query_binary_values('CURVE?', datatype='s')
        #print(self.osc1.query('DATA?'))

        # Acquire Measurement Data from waveform
        self.osc1.write('MEASUREMENT:IMMED:SOURCE CH' + str(CH_num))
        self.osc1.write('MEASUREMENT:IMMED:TYPE MINIMUM')
        Low_Wav = float(self.osc1.query('MEASUREMENT:IMMED:VALUE?'))

        self.osc1.write('MEASUREMENT:IMMED:TYPE MAX')
        Max_Wav = float(self.osc1.query('MEASUREMENT:IMMED:VALUE?'))

        # Format data
        array_wavefm = pd.Series(buffer)
        proc1_wavefm = array_wavefm - array_wavefm.min()
        proc2_wavefm = (proc1_wavefm / proc1_wavefm.max()) * (Max_Wav - Low_Wav)
        series_wave = proc2_wavefm + Low_Wav

        # Capture sample point time
        time_start = float(self.osc1.query('WFMOUTPRE:XZero?'))
        time_space = float(self.osc1.query('WFMOUTPRE:XINCR?'))
        time_sig = np.arange(0, time_space * len(array_wavefm), time_space) + np.ones(len(array_wavefm)) * time_start

        actual_wave = pd.DataFrame({'Time': time_sig,
                                    ('CH' + str(CH_num)): series_wave})

        # Time and Date Capture
        print(self.curr_time.strftime('%Y-%m-%d %H:%M:%S') + " Oscilloscope Wave on CH." + str(CH_num) + " captured")
        return actual_wave

    def waveform_rms(self, CH_num):
        # Set Input Requirement
        self.osc1.write('DATA:SOURCE CH' + str(CH_num))  # Select CH
        self.osc1.write('DATA:RESOLUTION FULL')  # Set Data Resolution
        self.osc1.write('DATA:COMPOSITION COMPOSITE_YT')
        self.osc1.write('DATA:ENCDG SRPbinary')  # Set Data Encoding
        self.osc1.write('DATA:START 1')
        self.osc1.write('DATA:STOP 125000')

        # Acquire Waveform (RAW) From Oscilloscope
        buffer = self.osc1.query_binary_values('CURVE?', datatype='s')

        # Acquire RMS from waveform
        self.osc1.write('MEASUREMENT:IMMED:SOURCE CH' + str(CH_num))
        self.osc1.write('MEASUREMENT:IMMED:TYPE RMS')
        rms = float(self.osc1.query('MEASUREMENT:IMMED:VALUE?'))

        return rms
