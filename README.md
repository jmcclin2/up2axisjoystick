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

## x,y Position Types
The driver can return the x,y position in raw 0-65,534 u16 counts or in mult-tiered up/down/left/right states.

### Raw u16 Output
If using internal driver polling with application callback, set the callback_ret_raw parameter to True to receive 'raw' values.  The callback parameter will be a list containing two values. If using the manual polling mode, call GetRawCount() to return a list containing two values.  The first item in the list will be the raw x value (0-65,534) and the second item in the list will be the raw y value (0-65,534).  

With the joystick in resting centered position, the raw x,y values should each be approximately 1/2 the maximum count (i.e. [32,767, 32,767]).  Moving the joystick to the left or right should increase or decrease the x count depending on how your potentiometers are wired.  The same is true of the y count when moving the joystick up and down.  The exact count values of center, fully up/down, fully left/right will vary depending on several factors including the resolution of your system's A/D, A/D reference voltage range and quality of the potentiometers and joystick construction.  

### Mult-tiered up/down/left/right States
An alternative to raw x,y counts are multi-tiered up/down/left/right states.  In this 
