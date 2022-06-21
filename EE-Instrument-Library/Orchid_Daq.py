from OMEGA_Library import OM_USB_Thermo, OM_USB_ADC
# from Tektronix_Library import MSO3014, DPO2024B
# from BKPrecision_Load_Library import BK8500_Load
import pyvisa
import nidaqmx


# OM_USB_numb is 0 by default
insert_number = 0
# CHx_Init = OM_USB_Thermo(OM_USB_numb=insert_number)
CHx_Init = OM_USB_ADC(OM_USB_numb=insert_number)

# insert_channel from 0 up to 7
insert_channel = 0
# CH0_data = CHx_Init.temp_reading(channel=insert_channel)
CH0_data = CHx_Init.voltage_reading(channel=insert_channel)
print(CH0_data)

