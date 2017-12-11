"""
Smartplug: control your sonoff device using MQTT

This assumes to run under a custom firmware which contains the following
frozen modules:

  - uasyncio.core
  - asyn.py, aswitch.py [https://github.com/peterhinch/micropython-async]
  - mqtt_as [https://github.com/peterhinch/micropython-mqtt]
"""

from sonoff import LED, BUTTON
from machine import Pin, Signal
import uasyncio as asyncio
from aswitch import Pushbutton

LOOP = asyncio.get_event_loop()

class SmartPlug(object):

    led = Signal(Pin(LED, Pin.OUT), invert=True)
    button = Pushbutton(Pin(BUTTON, Pin.IN))

    def __init__(self):
        self.button.press_func(self.on_click)
        self.button.long_func(self.on_long_press)
        self.button.double_func(self.on_double_click)

    def on_click(self):
        print('click')

    def on_long_press(self):
        print('long press')

    def on_double_click(self):
        print('double click')

    async def main(self):
        i = 0
        while True:
            print('main', i)
            i += 1
            await asyncio.sleep(1)


if __name__ == '__main__':
    app = SmartPlug()
    LOOP.run_until_complete(app.main())
    print('exit')
