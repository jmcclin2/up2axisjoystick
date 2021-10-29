from micropython import const
from machine import ADC, Timer

# A/D Constants
A_D_DEFAULT_DEADZONE_COUNT = const(0x0500)
A_D_MIN_COUNT              = const(0x0000)
A_D_LVL1_COUNT             = const(0x2AAA)
A_D_LVL2_COUNT             = const(0x5554)
A_D_MID_COUNT              = const(0x7FFE)
A_D_LVL4_COUNT             = const(0xAAAA)
A_D_LVL5_COUNT             = const(0xD554)
A_D_MAX_COUNT              = const(0xFFFE)

X_VALUE_LIST_INDEX    = const(0)
Y_VALUE_LIST_INDEX    = const(1)

# Stick states
SS_CENTERED           = const(0x0000)
SS_UP_MIN             = const(0x0001)
SS_UP_MID             = const(0x0002)
SS_UP_MAX             = const(0x0004)
SS_DOWN_MIN           = const(0x0008)
SS_DOWN_MID           = const(0x0010)
SS_DOWN_MAX           = const(0x0020)
SS_LEFT_MIN           = const(0x0040)
SS_LEFT_MID           = const(0x0080)
SS_LEFT_MAX           = const(0x0100)
SS_RIGHT_MIN          = const(0x0200)
SS_RIGHT_MID          = const(0x0400)
SS_RIGHT_MAX          = const(0x0800)

SS_To_String    = { SS_CENTERED  :"SS_CENTERED",
                    SS_UP_MIN    :"SS_UP_MIN",
                    SS_UP_MID    :"SS_UP_MID",
                    SS_UP_MAX    :"SS_UP_MAX",
                    SS_DOWN_MIN  :"SS_DOWN_MIN",
                    SS_DOWN_MID  :"SS_DOWN_MID",
                    SS_DOWN_MAX  :"SS_DOWN_MAX",
                    SS_LEFT_MIN  :"SS_LEFT_MIN",
                    SS_LEFT_MID  :"SS_LEFT_MID",
                    SS_LEFT_MAX  :"SS_LEFT_MAX",
                    SS_RIGHT_MIN :"SS_RIGHT_MIN",
                    SS_RIGHT_MID :"SS_RIGHT_MID",
                    SS_RIGHT_MAX :"SS_RIGHT_MAX" }

class TwoAxisAnalogJoystick:
    """Micropython Two Axis Analog Joystick Input Class"""
    
    def __init__(self, x_adc_pin_num, y_adc_pin_num, polling_ms=1000, reverse_x=False, reverse_y=False, callback=None, callback_ret_raw=False, deadzone=A_D_DEFAULT_DEADZONE_COUNT):
        self.x_adc_pin_num = x_adc_pin_num
        self.y_adc_pin_num = y_adc_pin_num
        self.polling_ms = polling_ms
        self.callback = callback

        self.x_adc_pin = ADC(self.x_adc_pin_num)
        self.y_adc_pin = ADC(self.y_adc_pin_num)
        self.x_adc_count = 0
        self.y_adc_count = 0
        
        self.poll_timer = Timer(-1)
        
        self.range_lookup = [[SS_LEFT_MAX, SS_DOWN_MAX],
                             [SS_LEFT_MID, SS_DOWN_MID],
                             [SS_LEFT_MIN, SS_DOWN_MIN],
                             [SS_CENTERED, SS_CENTERED],
                             [SS_RIGHT_MIN, SS_UP_MIN],
                             [SS_RIGHT_MID, SS_UP_MID],
                             [SS_RIGHT_MAX, SS_UP_MAX]]
        
        if (reverse_x):
            self.ReverseX()
            
        if (reverse_y):
            self.ReverseY()
            
        self.callback_ret_raw = callback_ret_raw
        self.deadzone = deadzone
    
    def ReverseX(self):
        self.range_lookup[0][0] = SS_RIGHT_MAX
        self.range_lookup[1][0] = SS_RIGHT_MID
        self.range_lookup[2][0] = SS_RIGHT_MIN
        self.range_lookup[4][0] = SS_LEFT_MIN
        self.range_lookup[5][0] = SS_LEFT_MID
        self.range_lookup[6][0] = SS_LEFT_MAX
        
    def ReverseY(self):
        self.range_lookup[0][1] = SS_UP_MAX
        self.range_lookup[1][1] = SS_UP_MID
        self.range_lookup[2][1] = SS_UP_MIN
        self.range_lookup[4][1] = SS_DOWN_MIN
        self.range_lookup[5][1] = SS_DOWN_MID
        self.range_lookup[6][1] = SS_DOWN_MAX
        
    def __UpdateRawCount(self):
        self.x_adc_count = self.x_adc_pin.read_u16()
        self.y_adc_count = self.y_adc_pin.read_u16()
        
    def GetRawCount(self):
        self.__UpdateRawCount()
        raw = []
        raw.append(self.x_adc_count)
        raw.append(self.y_adc_count)
        return raw
        
    def GetCurrentState(self):         
        raw = self.GetRawCount()
        state = []
        
        for index in range(2):       
            if (A_D_MIN_COUNT <= raw[index] and raw[index] < A_D_LVL1_COUNT):
                state.append(self.range_lookup[0][index])
            elif (A_D_LVL1_COUNT <= raw[index] and raw[index] < A_D_LVL2_COUNT):
                state.append(self.range_lookup[1][index])
            elif (A_D_LVL2_COUNT <= raw[index] and raw[index] < (A_D_MID_COUNT - A_D_DEFAULT_DEADZONE_COUNT)):
                state.append(self.range_lookup[2][index])
            elif ((A_D_MID_COUNT - A_D_DEFAULT_DEADZONE_COUNT) <= raw[index] and raw[index] < (A_D_MID_COUNT + A_D_DEFAULT_DEADZONE_COUNT)):
                state.append(self.range_lookup[3][index])
            elif ((A_D_MID_COUNT + A_D_DEFAULT_DEADZONE_COUNT) <= raw[index] and raw[index] < A_D_LVL4_COUNT):
                state.append(self.range_lookup[4][index])
            elif (A_D_LVL4_COUNT <= raw[index] and raw[index] < A_D_LVL5_COUNT):
                state.append(self.range_lookup[5][index])
            else:
                state.append(self.range_lookup[6][index])
                    
        return state
        
    def __PollTimerExpired(self, timer):     
        if (self.callback_ret_raw):
            raw = self.GetRawCount()
            self.callback(raw)
        else:
            state = self.GetCurrentState()
            self.callback(state)
        
    def StartPolling(self):
        self.poll_timer.init(mode=Timer.PERIODIC, period=self.polling_ms, callback=self.__PollTimerExpired)
    
    def StopPolling(self):
        self.poll_timer.deinit()
        
    def StateToString(self, state):
        return SS_To_String[state]