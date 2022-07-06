import time
import nidaqmx
from nidaqmx.constants import LineGrouping
from nidaqmx.constants import Edge
from nidaqmx.constants import AcquisitionType
from nidaqmx import stream_readers
import pandas as pd
import numpy as np

class NIDAQ:
    '''
    Library for using NIDAQ
    Contains function to read voltage
    '''
    def readVoltage(device, channel, sample, sample_per_channel):
        '''
        :param device: DAQ device number (ex: cDAQ1Mod3 for NI9215 since it's in the third spot)
        :param channel: physical channel that sensor is connected to (ex: ai0)
        :return: voltage reading from device/channel
        '''
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(device + "/" + channel)
            task.timing.cfg_samp_clk_timing(sample, source="", active_edge=Edge.RISING,
                                            sample_mode=AcquisitionType.FINITE, samps_per_chan=sample_per_channel)
            #read voltage channel
            output = task.read(sample)
            #print(output)
            return output
