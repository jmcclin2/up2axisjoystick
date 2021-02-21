# micropython_two_axis_analog_joystick
Micropython two axis analog joystick driver.  
- Automatic x,y position polling with application callback or manual polling modes
- Reports position in either raw 0-65,534 u16 count or multi-tiered up/down/left/right states
- Independently reversible x and y axis to match wiring of joystick potentiometers
- Adjustable center 'dead zone'  

## Usage
There are two primary usage patterns: 1) internal driver polling of x,y position with application callback or 2) manual polling of x,y position from applicaiton.

### Internal Driver Polling of x,y Position With Application Callback
In this mode of operation the driver polls the x,y position at a specified rate and updates the application via a callback.

```python
from two_axis_analog_joystick import TwoAxisAnalogJoystick

# Joystick callback
def stick_cb(val):
    x = val[0]
    y = val[1]
    print("x count:", x)
    print("y count:", y)
    
# x potentiometer on pin 26, y potentiometer on pin 27, make measurement every 100ms and return raw x,y counts    
stick = TwoAxisAnalogJoystick(26, 27, polling_ms=100, callback=stick_cb, callback_ret_raw=True)
stick.StartPolling()

# ...
# stick.StopPolling()
```

### Manual Polling of x,y Position From Application
In this mode of operation the application polls the driver for the current x,y position.

```python
from two_axis_analog_joystick import TwoAxisAnalogJoystick
import time

# x potentiometer on pin 26, y potentiometer on pin 27    
stick = TwoAxisAnalogJoystick(26, 27)

while True:
    val = stick.GetRawCount()
    x = val[0]
    y = val[1]
    print("x count:", x)
    print("y count:", y)
    time.sleep(1)
```

## x,y Position Reporting Types
The driver can return the x,y position in raw 0-65,534 u16 counts or in mult-tiered up/down/left/right states.

### Raw u16 Output
If using internal driver polling with application callback, set the callback_ret_raw parameter to True to receive 'raw' values.  The callback parameter will be a list containing two values. If using the manual polling mode, call GetRawCount() to return a list containing two values.  The first item in the list will be the raw x value (0-65,534) and the second item in the list will be the raw y value (0-65,534).  

With the joystick in resting centered position, the raw x,y values should each be approximately 1/2 the maximum count (i.e. [32,766, 32,766]).  Moving the joystick to the left or right should increase or decrease the x count depending on how your potentiometers are wired.  The same is true of the y count when moving the joystick up and down.  The exact count values of center, fully up/down, fully left/right will vary depending on several factors including the resolution of your system's A/D, A/D reference voltage range and quality of the potentiometers and joystick construction.  

### Mult-tiered up/down/left/right States
An alternative to raw x,y counts are multi-tiered up/down/left/right states.  In this mode each cardinal direction (up/down/left/right) is split into three equally\* sized regions, Zone 1, Zone 2, and Zone 3 (see **Image 1**).  

\*The Dead Zone lies at the very center and is subtracted from the total size of Zone 1.

![two_axis_analog_joystick_zones](/images/two_axis_analog_joystick_zones.png) |
----------------------- |
**Image 1: Joystick Zones** |

The divisions between the zones are determined by the values of x1-x8 and y1-y8 (see **Image 2**).

![two_axis_analog_joystick_values](/images/two_axis_analog_joystick_values.png) |
----------------------- |
**Image 2: Zone Values** |
 
In its default state, the driver assigns the following values to x1-x8 and y1-y8:
Marker        | Raw Count Value       |
------------- | --------------------- |
  x1, y1      |   0x0000 (0d)         |
  x2, y2      |   0x2AAA (10,922d)    |
  x3, y3      |   0x5554 (21,844d)    |
  x4, y4      |   0x7AFE (31,486d)    |
  center      |   0x7FFE (32,766d)    |
  x5, y5      |   0x84FE (34,046d)    |
  x6, y6      |   0xAAAA (43,690d)    |
  x7, y7      |   0xD554 (54,612d)    |
  x8, y8      |   0xFFFE (65,534d)    |

The x and y states are determined independently depending on which zone the coordinates lie between when measured.  States corresponding to x will be LOW/MED/HIGH variants of LEFT and RIGHT.  States corresponding to y will be LOW/MED/HIGH variants of UP and DOWN.  When the x,y coordinates lie in the dead zone the CENTERED state is returned. 

* Zone 3 
  * If x1 <= x_measured < x2 then ```SS_LEFT_HI``` stick state is returned
  * If y1 <= y_measured < y2 then ```SS_DOWN_HI``` stick state is returned
  * If x7 <= x_measured <= x8 then ```SS_RIGHT_HI``` stick state is returned
  * If y7 <= y_measured <= y8 then ```SS_UP_HI``` stick state is returned

* Zone 2 
  * If x2 <= x_measured < x3 then ```SS_LEFT_MED``` stick state is returned
  * If y2 <= y_measured < y3 then ```SS_DOWN_MED``` stick state is returned
  * If x6 <= x_measured < x7 then ```SS_RIGHT_MED``` stick state is returned
  * If y6 <= y_measured < y7 then ```SS_UP_MED``` stick state is returned

* Zone 1 
  * If x3 <= x_measured < x4 then ```SS_LEFT_LOW``` stick state is returned
  * If y3 <= y_measured < y4 then ```SS_DOWN_LOW``` stick state is returned
  * If x5 <= x_measured < x6 then ```SS_RIGHT_LOW``` stick state is returned
  * If y5 <= y_measured < y6 then ```SS_UP_LOW``` stick state is returned

* Dead Zone
  * If x4 <= x_measured < x5 then ```SS_CENTERED``` stick state is returned
  * If y4 <= y_measured < y5 then ```SS_CENTERED``` stick state is returned
