"""
Smartplug: control your sonoff device using MQTT

This assumes to run under a custom firmware which contains the following
frozen modules:

  - uasyncio.core
  - asyn.py, aswitch.py [https://github.com/peterhinch/micropython-async]
  - mqtt_as [https://github.com/peterhinch/micropython-mqtt]
"""

from sonoff import LED, BUTTON, RELAY
from machine import Pin, Signal
import uasyncio as asyncio
from aswitch import Pushbutton

LOOP = asyncio.get_event_loop()

class SmartPlug(object):

    led = Signal(Pin(LED, Pin.OUT, value=0), invert=True)
    relay = Signal(Pin(RELAY, Pin.OUT, value=0))
    button = Pushbutton(Pin(BUTTON, Pin.IN))

    def __init__(self):
        self.button.press_func(self.on_click)
        self.button.long_func(self.on_long_press)
        self.button.double_func(self.on_double_click)
        self.status = False

    @property
    def status(self):
        """
        The status of the switch. The invariant is that the following are always
        in sync:
          - the status led
          - the relay
        """
        return self._status

    @status.setter
    def status(self, v):
        print ("setting status to", v)
        self._status = v
        self.led.value(v)
        self.relay.value(v)

    def on_click(self):
        self.status = not self.status

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
