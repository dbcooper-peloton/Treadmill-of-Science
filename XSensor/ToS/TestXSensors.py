import ctypes
import XSCore90
import XSNReader
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)
XSCore90.XS_InitLibrary(1)

XSNfp = r'C:\Users\AndyKind\Documents\GitHub\Project-Orchid\XSensor\ToS\testScripts\X_Log.XSN'
Calfp = r'C:\Users\AndyKind\Documents\GitHub\Project-Orchid\XSensor\ToS\Calibration'

pressure = ctypes.c_float()
minPressureRange = ctypes.c_float()
maxPressureRange = ctypes.c_float()
units = ctypes.c_ubyte()
X4Error = ctypes.c_uint()
XSNError = ctypes.c_uint()

# Tell the DLL to find any Bluetooth X4 sensors - only do this if you are using Bluetooth - slow otherwise)
XSCore90.XS_SetAllowX4Wireless(1);
XSCore90.XS_SetX4Mode8Bit(1);
XSCore90.XS_SetStreamingMode(1);

# Ask the DLL to scan the computer for attached sensors. Returns the number of sensors found.
nbrSensors = XSCore90.XS_EnumSensors()
lastEnumState = XSCore90.XS_GetLastEnumState()
sMesg = 'Found ' + str(nbrSensors) + ' sensors; ' + 'Last Enumeration State: ' + str(lastEnumState) + '\n'
print(sMesg)

XSCore90.XS_SetCalibrationFolder(Calfp)
# Build a sensor configuration. The DLL must be told which sensors to use.
if nbrSensors > 0:
    sMesg = 'Building sensor configuration...'
    print(sMesg)
    nbrSensors = 0

    # This will automatically configure all sensors on the computer
    if XSCore90.XS_AutoConfigXSN(XSNfp, XSCore90.EPressureUnit.ePRESUNIT_PSI.value, -1.0) == 1:
        nbrSensors = XSCore90.XS_ConfigSensorCount()
        sMesg = 'Configured ' + str(nbrSensors) + ' sensors\n'
        print(sMesg)

XSCore90.XS_GetPressureUnit(ctypes.byref(units))
print('Unit Code 1: ' + str(units.value))
XSCore90.XS_SetPressureUnit(ctypes.c_ubyte(XSCore90.EPressureUnit.ePRESUNIT_KGCM2.value))
XSCore90.XS_GetPressureUnit(ctypes.byref(units))
print('Unit Code 2: ' + str(units.value))
XSCore90.XS_SetPressureUnit(ctypes.c_ubyte(XSCore90.EPressureUnit.ePRESUNIT_PSI.value))
XSCore90.XS_GetPressureUnit(ctypes.byref(units))
print('Unit Code 3: ' + str(units.value) +'\n')

if XSCore90.XS_OpenConnection(9000) == 1:
    for x in range(10):
        if x % 2 == 1:
            XSCore90.XS_SetPressureUnit(ctypes.c_ubyte(XSCore90.EPressureUnit.ePRESUNIT_KGCM2.value))
        else:
            XSCore90.XS_SetPressureUnit(ctypes.c_ubyte(XSCore90.EPressureUnit.ePRESUNIT_PSI.value))
        print(str(XSCore90.XS_GetPressureUnit()))
    XSCore90.XS_CloseConnection()
    XSCore90.XS_ExitLibrary()
    XSNReader.XSN_InitLibrary()
    if XSNReader.XSN_LoadSessionU(XSNfp):
        sMesg = 'Session base pressure units is ' + str(XSNReader.XSN_GetPressureUnits())
        print(sMesg)
        sMesg = 'Session base force units is ' + str(XSNReader.XSN_GetForceUnits())
        print(sMesg)
        XSNReader.XSN_CloseSession()
        XSNReader.XSN_ExitLibrary()
    else:
        print("failed to open XSN file")
