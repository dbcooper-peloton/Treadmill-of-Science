from OMEGA_Library import OM_USB_Thermo, OM_USB_ADC
from Tektronix_Library import MSO3014, DPO2024B
from BKPrecision_Load_Library import BK8500_Load
import pyvisa
import nidaqmx

'''
Example code to extract waveform in Pandas Dataframe format from:
- Tektronix DPO2024B
- Tektronix MSO3014
'''
'''
rm = pyvisa.ResourceManager()
list_dev = rm.list_resources()

p1 = DPO2024B(list_dev[0])
p2 = MSO3014(list_dev[0])

p1.oscilloscope_ID()
p2.oscilloscope_ID()

# Get Waveform and Data formatted in Pandas DataFrame
Channel_number = 1
p1_waveform_array = p1.waveform_RAW(Channel_number)
p2_waveform_array = p2.waveform_RAW(Channel_number)

'''
'''
Example code to set BKPrecision DC Load to specific parameters:
- Current (Coming soon)
- Voltage (Coming soon)
- Power
- Resistance (Coming soon)
'''
'''
BKLoad = BK8500_Load('COM3', 4800)
BKLoad.set_RemoteModeON()
BKLoad.set_LoadOFF()
BKLoad.set_OperationMode('CW')
BKLoad.set_Power(17)
BKLoad.set_LoadON()
BKLoad.set_RemoteModeOFF()

BKLoad.close()
'''
'''
Example code to extract singular Thermal datapoint in Celcius from:
- OMEGA OM_USB_TC
'''

# OM_USB_numb is 0 by default
insert_number = 0
# CHx_Init = OM_USB_Thermo(OM_USB_numb=insert_number)
CHx_Init = OM_USB_ADC(OM_USB_numb=insert_number)

# insert_channel from 0 up to 7
insert_channel = 0
# CH0_data = CHx_Init.temp_reading(channel=insert_channel)
CH0_data = CHx_Init.voltage_reading(channel=insert_channel)
print(CH0_data)
