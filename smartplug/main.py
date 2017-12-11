"""
Smartplug: control your sonoff device using MQTT

This assumes to run under a custom firmware which contains the following
frozen modules:

  - uasyncio.core
  - asyn.py, aswitch.py [https://github.com/peterhinch/micropython-async]
  - mqtt_as [https://github.com/peterhinch/micropython-mqtt]
"""

from machine import Pin, Signal
from network import WLAN, STA_IF
from sonoff import LED, BUTTON, RELAY
import uasyncio as asyncio
from aswitch import Pushbutton
import mqtt_as
mqtt_as.sonoff()  # ugly way to turn on sonoff-specific behavior

mqtt_as.MQTTClient.DEBUG = True
LOOP = asyncio.get_event_loop()
SERVER = 'test.mosquitto.org'

def MQTTClient(**kwargs):
    """
    Saner API to construct an MQTTClient
    """
    config = mqtt_as.config.copy()
    config.update(kwargs)
    return mqtt_as.MQTTClient(config)

class SmartPlug(object):

    led = Signal(Pin(LED, Pin.OUT, value=0), invert=True)
    relay = Signal(Pin(RELAY, Pin.OUT, value=0))
    button = Pushbutton(Pin(BUTTON, Pin.IN))

    def __init__(self):
        self.mqtt = MQTTClient(
            server=SERVER,
            keepalive=120,
            clean=True,
            clean_init=True,
            )
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

    async def wait_for_connection(self):
        print('[MQTT] Connecting...')
        sta_if = WLAN(STA_IF)
        conn = False
        while not conn:
            while not sta_if.isconnected():
                print('[MQTT] Waiting for WiFi...')
                await asyncio.sleep(1)
            print('[MQTT] WiFi connected, waiting some more...')
            await asyncio.sleep(3)
            try:
                await self.mqtt.connect()
                conn = True
            except OSError:
                self.mqtt.close()  # Close socket
                print('[MQTT] Waiting for server...')
        print('[MQTT] Connected')

    async def main(self):
        LOOP.create_task(self.wait_for_connection())
        i = 0
        while True:
            print('main', i)
            i += 1
            await asyncio.sleep(1)


if __name__ == '__main__':
    app = SmartPlug()
    LOOP.run_until_complete(app.main())
    print('exit')
