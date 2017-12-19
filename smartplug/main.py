"""
Smartplug: control your sonoff device using MQTT

This assumes to run under a custom firmware which contains the following
frozen modules:

  - uasyncio.core
  - asyn.py, aswitch.py [https://github.com/peterhinch/micropython-async]
  - mqtt_as [https://github.com/peterhinch/micropython-mqtt]
"""

import time
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

def fmtime(t=None):
    """
    Smart time format
    """
    if t is None:
        t = time.localtime()
    elif isinstance(t, int):
        t = time.localtime(t)
    elif isinstance(t, tuple):
        pass # nothing to do
    else:
        raise TypeError("Expected None, int or tuple")
    #
    return '%d-%02d-%02d %02d:%02d:%02d' % t[:6]


class SmartPlug(object):

    led = Signal(Pin(LED, Pin.OUT, value=0), invert=True)
    relay = Signal(Pin(RELAY, Pin.OUT, value=0))
    button = Pushbutton(Pin(BUTTON, Pin.IN))

    # default value so that .log() works even before mqtt has been created
    mqtt = None

    def __init__(self, topic):
        assert isinstance(topic, bytes)
        self.topic = topic
        self.log_topic = topic + b'/log'
        self.wifi_connected = False
        #
        # initialize status BEFORE starting mqtt: this way, as soon as the
        # first retained message arrives, we are ready to handle it
        self.set_status(False, should_publish=False)
        self.status_received = False
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

    def log(self, *args):
        msg = ' '.join(map(str, args))
        print(msg)
        if self.mqtt:
            LOOP.create_task(self.mqtt.publish(self.log_topic, msg))

    @property
    def status(self):
        """
        The status of the switch. The invariant is that the following are always
        in sync:
          - the status led
          - the relay
          - the mqtt topic (which is retained)
        """
        return self._status

    def set_status(self, v, should_publish):
        self.log("[STAT] set status to", v)
        self._status = v
        self.led.value(v)
        self.relay.value(v)
        if should_publish:
            self.publish_status()

    def publish_status(self):
        msg = str(int(self.status))
        self.log('[PUB ]', self.topic, msg)
        LOOP.create_task(self.mqtt.publish(self.topic, msg, retain=True,
                                           qos=QOS_AT_LEAST))

    def on_receive_topic(self, topic, msg):
        self.log('[SUB ] received', topic, msg)
        if topic == self.topic:
            try:
                value = int(msg)
            except ValueError:
                self.log('[SUB ] invalid value, defaulting to 0')
                value = 0
            #
            self.status_received = True
            if self.status == value:
                self.log("[SUB ] status already %s, ignoring" % value)
                return
            self.log('[SUB ] setting status to', value)
            self.set_status(value, should_publish=False)

    def on_click(self):
        self.set_status(not self.status, should_publish=True)

    def on_long_press(self):
        print('long press')

    def on_double_click(self):
        print('double click')

    async def wait_for_connection(self):
        self.log('[MQTT] Connecting...')
        sta_if = WLAN(STA_IF)
        conn = False
        while not conn:
            while not sta_if.isconnected():
                self.log('[MQTT] Waiting for WiFi...')
                await asyncio.sleep(1)
            self.wifi_connected = True
            self.log('[MQTT] WiFi connected, waiting some more...')
            await asyncio.sleep(3)
            try:
                await self.mqtt.connect()
                conn = True
            except OSError:
                self.mqtt.close()  # Close socket
                self.log('[MQTT] Waiting for server...')
        self.log('[MQTT] Connected')
        await self.mqtt.subscribe(self.topic, QOS_AT_LEAST)

    async def timer(self):
        import ntptime
        # first, wait for wifi connection and set time
        while not self.wifi_connected:
            self.log('[TIME] Waiting for Wifi...')
            await asyncio.sleep(1)
        #
        self.log('[TIME] setting NTP time')
        ntptime.settime()
        self.log('[TIME] UTC time: %s' % fmtime())
        while True:
            t = time.time()
            self.log('[TIME] woke up at %s' % fmtime(t))
            y, m, d, hh, mm, ss = time.localtime(t)[:6]
            # turn the lights on between 17 and 1 CEST, i.e. 16-24 UTC
            should_be_on = hh >= 16
            if self.status != should_be_on:
                self.log('[TIME] changing status')
                self.set_status(should_be_on, should_publish=True)
            #
            # now, determine how much to sleep before next change
            if should_be_on:
                # wait until next day: to determine it, we do 23:59:59 + 1 second
                t_end = time.mktime((y, m, d, 23, 59, 59, None, None)) + 1
            else:
                # wait until 16 of the current day
                t_end = time.mktime((y, m, d, 16, 0, 0, None, None))
            t_diff = t_end - t
            self.log('[TIME] sleeping for %d seconds, until %s' % (t_diff, fmtime(t_end)))
            await asyncio.sleep(t_diff)

    async def main(self):
        LOOP.create_task(self.wait_for_connection())
        LOOP.create_task(self.timer())
        i = 0
        while True:
            self.log('[MAIN]', i)
            #
            # periodically publish the status, but ONLY if we received at
            # least one message from the broker. Else, at startup we send 0
            # before we had the chance to receive the reatined message
            if self.status_received and i % 12 == 0: # once every 60 seconds
                self.publish_status()
            i += 1
            await asyncio.sleep(5)


if __name__ == '__main__':
    app = SmartPlug(b'/antocuni/xmas')
    LOOP.run_until_complete(app.main())
    print('exit')
