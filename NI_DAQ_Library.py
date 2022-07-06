import time
import nidaqmx
from nidaqmx.constants import LineGrouping
from nidaqmx.constants import Edge
from nidaqmx.constants import AcquisitionType

class NIDAQ:
    '''
    Library for using NIDAQ
    Contains function to read voltage
    '''
    def readVoltage(device, channel, sample):
        '''
        :param device: DAQ device number (ex: cDAQ1Mod3 for NI9215 since it's in the third spot)
        :param channel: physical channel that sensor is connected to (ex: ai0)
        :return: voltage reading from device/channel
        '''
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(device + "/" + channel)
            task.timing.cfg_samp_clk_timing(sample, source="", active_edge=Edge.RISING,
                                            sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=sample)
            #read voltage channel
            output = task.read(sample)
            #print(output)
            return output

    def readVoltage1(device, channel):
        '''
        :param device: DAQ device number (ex: cDAQ1Mod3 for NI9215 since it's in the third spot)
        :param channel: physical channel that sensor is connected to (ex: ai0)
        :return: voltage reading from device/channel
        '''
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(device + "/" + channel)
            task.timing.cfg_samp_clk_timing(1000, source="", active_edge=Edge.RISING,
                                            sample_mode=AcquisitionType.CONTINUOUS, samps_per_chan=1000)
            #read voltage channel
            output = task.read(1000)
            #print(output)
            return output

