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
    import time
    import network
    sta_if = network.WLAN(network.STA_IF)
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
    print('connecting to %s...' % ssid)
    blink(2)
    sta_if.active(True)
    timeout *= 1000 # convert from seconds to ms
    start_time = time.ticks_ms()
    sta_if.connect(ssid, password)
    while not sta_if.isconnected():
        cur_time = time.ticks_ms()
        if time.ticks_diff(cur_time, start_time) > timeout:
            print('connection timed out, giving up')
            sta_if.disconnect()
            return
    print('network config:', sta_if.ifconfig())

def auto_connect():
    try:
        with open('wifi.ini') as f:
            content = f.read().strip()
    except IOError:
        print('cannot read wifi.ini, skipping Wi-Fi connection')
    else:
        ssid, password = content.split(' ')
        print('Wi-Fi auto-connect: %s' % ssid)
        connect_wifi(ssid, password)

# if you want to enable Wi-Fi auto-connect, simply put a wifi.ini with only
# one line
#    ssid password
auto_connect()
