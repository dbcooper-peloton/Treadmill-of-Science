from mcculw import ul
from mcculw.enums import TempScale, TInOptions, ULRange

class OM_USB_Thermo:
    '''
    Initialization command:
    - Detect board on CH number defined on variable OM_USB_numb (0 default)
    - Return the board name that was detected
    Commands:
    - temp_reading(channel) = Take ONE temperature reading from channel defined.
    '''
    def __init__(self, OM_USB_numb):
        self.board_numb = OM_USB_numb
        self.board_name = ul.get_board_name(board_num=OM_USB_numb)
        print("Board Found: " + self.board_name)
    def temp_reading(self, channel):
        #Read data from selected channel:
        Temp_value = ul.t_in(self.board_numb, channel, TempScale.CELSIUS, TInOptions.NOFILTER)
        return Temp_value

class OM_USB_ADC: #use this class for voltage outputs
    '''
    Initialization command:
    - Detect board on CH number defined on variable OM_USB_numb (0 default)
    - Return the board name that was detected
    '''
    def __init__(self, OM_USB_numb):
        self.board_numb = OM_USB_numb
        self.board_name = ul.get_board_name(board_num=OM_USB_numb)
        print("Board Found: " + self.board_name)
    def voltage_reading(self, channel):
        '''
        untested
        '''
        #Read analog data from selected channel:
        value_in = ul.v_in(self.board_numb, channel, ULRange.BIP10VOLTS)
        return value_in
