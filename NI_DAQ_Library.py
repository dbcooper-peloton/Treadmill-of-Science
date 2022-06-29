import nidaqmx

class NIDAQ:
    '''
    Library for using NIDAQ
    Contains function to read voltage
    '''
    def readVoltage(device, channel):
        '''
        :param device: DAQ device number (ex: cDAQ1Mod3 for NI9215 since it's in the third spot)
        :param channel: physical channel that sensor is connected to (ex: ai0)
        :return: voltage reading from device/channel
        '''
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(device + "/" + channel)
            task.timing.cfg_samp_clk_timing(2000)
            #read voltage channel
            output = task.read()    #voltage reading
            #print(output)
            return output


    #print(readVoltage('cDAQ1Mod3', 'ai0'))



