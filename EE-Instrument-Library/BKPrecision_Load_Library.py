import serial

class BK8500_Load:
    '''
    Initialization command:
    - Connect to BKPrecision DC Load
    - Check for Connection

    Commands:
    - set_LoadOFF() = Set the DC Load OFF (Before Changing the Load Setting)
    - set_LoadON() = Set the DC Load ON (To start drawing power)
    - set_RemoteModeON() = Set Remote Mode to Control through Serial
    - set_RemoteModeOFF() = To control through front panel
    - set_OperationMode(Mode) = Set operation mode to CC, CV, CW or CR
    - set_Power(Nominal Power) = Set power mode to Nominal Power value
    - close() = Close serial operations
    '''
    def __init__(self, com_port, baud_rate):
        self.ser = serial.Serial(port=com_port, baudrate=baud_rate)
        if (self.ser.is_open):
            print('DC Load Connected')
        else:
            print('DC Load Undetected')

    def printbuff(self, b):
        r = ""
        for s in range(26):
            r += "|"
            r += str(s)
            r += "-"
            r += hex(b[s])
        print(r)

    def cmd8500(self, cmd):
        print('Sending message...')
        #print('message: ')
        #self.printbuff(cmd)

        self.ser.write(cmd)

        resp = self.ser.read(26)
        print('response: ')
        self.printbuff(resp)

        # TODO: Test if working or not
        if resp[3] == 0x90:
            print('Checksum incorrect \n')
        elif resp[3] == 0xA0:
            print('Parameter incorrect \n')
        elif resp[3] == 0xB0:
            print('Unrecognized command \n')
        elif resp[3] == 0xC0:
            print('Invalid command \n')
        elif resp[3] == 0x80:
            print('Command was successful \n')

    def set_RemoteModeON(self):
        self.cmd8500(([0xaa,00,0x20,0x01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,0xcb]))

    def set_RemoteModeOFF(self):
        self.cmd8500(([0xaa,00,0x20,0x00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,0xca]))

    def set_LoadON(self):
        message = ([0xaa,00,0x21,0x01,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,0xCC])
        self.cmd8500(message)

    def set_LoadOFF(self):
        message = ([0xaa,00,0x21,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,0xCB])
        self.cmd8500(message)

    def set_OperationMode(self, mode):
        ser_message = ([0xaa,00,0x28,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00])

        if mode == 'CC' or mode == 'cc':
            hex_mode = 0x00
        elif mode == 'CV' or mode == 'cv':
            hex_mode = 0x01
        elif mode == 'CW' or mode == 'cw':
            hex_mode = 0x02
        elif mode == 'CR' or mode == 'cr':
            hex_mode = 0x03

        ser_message[3] = hex_mode
        ser_message[25] = int(hex(0xaa + 0x28 + hex_mode), 16)

        self.cmd8500(ser_message)

    def set_Power(self, power_dec):
        ser_message = ([0xaa, 00, 0x2E, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 00, 0xD2])

        # Convert Decimal Power Value to HEX
        power_hex = hex(int(power_dec * 1000))
        power_formatHex = power_hex[2:len(power_hex)]

        # Format Power HEX Value
        Hex_format = []
        i = len(power_formatHex) - 1
        while i >= 0:
            Hex_format.append(str('0x' + power_formatHex[i - 1] + power_formatHex[i]))
            i = i - 2

        # Enter Power HEX (integer) to Serial Message
        for i in range(0, len(Hex_format)):
            ser_message[i + 3] = int(Hex_format[i], 16)

        # Adjust Checksum
        checksum = hex(sum(ser_message[0:len(ser_message) - 1]))
        checksum_str = str('0x' + checksum[len(checksum) - 2:len(checksum)])
        checksum_hex = int(checksum_str, 16)

        ser_message[len(ser_message) - 1] = checksum_hex

        self.cmd8500(ser_message)

    def close(self):
        self.ser.close()