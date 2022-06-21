# EE-Instrument-Library
PELOTON/PRECOR USE ONLY

Python Libraries to interface to Precor/Peloton electrical instruments

Python Library Needed:
  - Pandas
  - Numpy
  - PyVisa
  - datetime
  - openpyxl
  - mcculw
  - PySerial

To download all libraries in used in the Instrument Library:

- Run ```Python Library Init.bat```

List of equipment available to interface to:
- Tektronix MSO3014
    ````                                    
    p1 = MSO3014(USB ID)                   
                                              
    p1.oscilloscope_ID()                    
    p1.waveform_RAW(Channel_number)         
    ````                                    
- Tektronix DPO2024B
    ````                            
    p1 = DPO2024B(USB ID)           
                                    
    p1.oscilloscope_ID()                                 
    p1.waveform_RAW(Channel_number) 
    ````                            
- OMEGA USB_OM_TC Thermometer
    ```
    CHx_Init = OM_USB_Thermo(0) 
  
    CH0_data = CHx_Init.temp_reading(channel=0)
    CH1_data = CHx_Init.temp_reading(channel=1)  
    ```
- BKPrecision DC Load 8500 series
    ```
    BKLoad = BK8500_Load('COM3', 4800)
  
    # Set Load OFF
    BKLoad.set_LoadOFF()
  
    # Enable remote on
    BKLoad.set_RemoteModeON()
    
    # Set to CW Mode
    BKLoad.set_OperationMode('CV', 'CR', CW' or 'CC')

    # Set Power to Nominal
    # example
    NominalValue = 13
    BKLoad.set_Power(NominalValue)
  
    # Set Load ON  
    BKLoad.set_LoadON()
   
    # front panel ON
    BKLoad.set_RemoteModeOFF()
  
    BKLoad.close()
  ```  
