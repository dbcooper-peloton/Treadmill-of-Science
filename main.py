from OMEGA_Library import OM_USB_Thermo, OM_USB_ADC
from csv import writer
from NI_DAQ_Library import NIDAQ
from Tektronix_Library import DPO2024B
import pyvisa


def OMEGA_DAQ():
    # OM_USB_numb is 0 by default
    insert_number = 0
    # CHx_Init = OM_USB_Thermo(OM_USB_numb=insert_number)
    CHx_Init = OM_USB_ADC(OM_USB_numb=insert_number)

    # insert_channel from 0 up to 7
    insert_channel = 0
    # CH0_data = CHx_Init.temp_reading(channel=insert_channel)
    CH0_data = CHx_Init.voltage_reading(channel=insert_channel)
    #print(CH0_data)

    CH1_data = CHx_Init.voltage_reading(channel=1)
    CH2_data = CHx_Init.voltage_reading(channel=2)
    CH3_data = CHx_Init.voltage_reading(channel=3)
    CH4_data = CHx_Init.voltage_reading(channel=4)
    CH5_data = CHx_Init.voltage_reading(channel=5)
    CH6_data = CHx_Init.voltage_reading(channel=6)
    CH7_data = CHx_Init.voltage_reading(channel=7)

    print("Channel 0: " + str(CH0_data))
    print("Channel 1: " + str(CH1_data))
    print("Channel 2: " + str(CH2_data))
    print("Channel 3: " + str(CH3_data))
    print("Channel 4: " + str(CH4_data))
    print("Channel 5: " + str(CH5_data))
    print("Channel 6: " + str(CH6_data))
    print("Channel 7: " + str(CH7_data))

def writeToCSV():
    Header = ['CH0_data', 'CH1_data', 'CH2_data', 'CH3_data', 'CH4_data', 'CH5_data', 'CH6_data', 'CH7_data']
    Data = [CH0_data, CH1_data, CH2_data, CH3_data, CH4_data, CH5_data, CH6_data, CH7_data]

    with open('event.csv', 'w', newline='') as f_object:
        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object)

        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(Header)
        writer_object.writerow(Data)

        # Close the file object
        f_object.close()


def tek_scope():
    rm = pyvisa.ResourceManager()
    list_dev = rm.list_resources()
    # Set device
    p1 = DPO2024B(list_dev[0])
    # Get device ID
    p1.oscilloscope_ID()
    Channel_number = 1
    # retrieve rms from the waveform and return it
    return p1.waveform_rms(Channel_number)


