"""
Smartplug: control your sonoff device using MQTT

This assumes to run under a custom firmware which contains the following
frozen modules:

  - uasyncio.core
  - asyn.py, aswitch.py [https://github.com/peterhinch/micropython-async]
  - mqtt_as [https://github.com/peterhinch/micropython-mqtt]
"""

from micropython import const
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

QOS_AT_MOST = const(0)
QOS_AT_LEAST = const(1)
QOS_EXACT = const(2)

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

    def __init__(self, topic):
        assert isinstance(topic, bytes)
        self.topic = topic
        self.mqtt = MQTTClient(
            server=SERVER,
            keepalive=120,
            clean=True,
            clean_init=True,
            subs_cb=self.on_receive_topic,
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
        print("[STAT] set status to", v)
        self._status = v
        self.led.value(v)
        self.relay.value(v)
        self.publish(self.topic, str(int(v)))

    def publish(self, topic, msg):
        print('[PUB ]', topic, msg)
        LOOP.create_task(self.mqtt.publish(topic, msg, qos=QOS_AT_LEAST))

    def on_receive_topic(self, topic, msg):
        print('[SUB ] received', topic, msg)
        if topic == self.topic:
            try:
                value = int(msg)
            except ValueError:
                print('[SUB ] invalid value, defaulting to 0')
                value = 0
            if self.status != value:
                print('[SUB ] setting status to', value)
                self.status = value

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
        await self.mqtt.subscribe(self.topic, QOS_AT_LEAST)

    async def main(self):
        LOOP.create_task(self.wait_for_connection())
        i = 0
        while True:
            print('[MAIN]', i)
            i += 1
            await asyncio.sleep(5)


if __name__ == '__main__':
    app = SmartPlug(b'/antocuni/xmas')
    LOOP.run_until_complete(app.main())
    print('exit')
