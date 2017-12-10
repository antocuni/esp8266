# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#
# enable webrepl
## import gc
## import webrepl
## webrepl.start()
## gc.collect()

import sys
sys.path.append('libs')
from wemos_d1 import blink

def connect_wifi(ssid, password, timeout=10):
    try:
        _connect_wifi(ssid, password, timeout)
    finally:
        blink(0)

def _connect_wifi(ssid, password, timeout):
    import network
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if sta_if.isconnected():
        print('wlan already connected')
        print('network config:', sta_if.ifconfig())
        return

    print('Scanning for available Wi-Fi networks...')
    blink(1)
    ssids = [tup[0] for tup in sta_if.scan()]
    print(len(ssids), 'networks found:')
    for name in ssids:
        print('   ', name)
    print()
    #
    if ssid.encode('latin1') not in ssids:
        print('SSID %s not found' % ssid)
        return
    #
    sta_if.connect(ssid, password)
    if timeout > 0 and _wait_for_connection(sta_if, ssid, timeout):
        print('network config:', sta_if.ifconfig())

def _wait_for_connection(sta_if, ssid, timeout):
    import time
    blink(2)
    timeout *= 1000 # convert from seconds to ms
    start_time = time.ticks_ms()
    next_print = start_time
    i = 0
    while not sta_if.isconnected():
        # this sleep seems to be necessary on my sonoff device. On the other
        # hand, on the wemos D1 it connected even without it, no clue why
        time.sleep_ms(10)
        cur_time = time.ticks_ms()
        if time.ticks_diff(cur_time, start_time) >= timeout:
            print('connection timed out, giving up')
            sta_if.disconnect()
            return False
        if time.ticks_diff(cur_time, next_print) >= 0:
            i += 1
            next_print = time.ticks_add(cur_time, 1000)
            print('connecting to %s... [%d]' % (ssid, i))
    return True


def auto_connect(timeout=10):
    try:
        with open('wifi.ini') as f:
            content = f.read().strip()
    except OSError:
        print('cannot read wifi.ini, skipping Wi-Fi connection')
    else:
        ssid, password = content.split(' ')
        print('Wi-Fi auto-connect: %s' % ssid)
        connect_wifi(ssid, password, timeout=timeout)

# if you want to enable Wi-Fi auto-connect, simply put a wifi.ini with only
# one line
#    ssid password
auto_connect(timeout=0)
