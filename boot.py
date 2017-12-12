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
import machine
sys.path.append('libs')
from led import blink

def connect_wifi(netdb, timeout=10):
    try:
        _connect_wifi(netdb, timeout)
    finally:
        blink(0)

def _connect_wifi(netdb, timeout):
    # lazy import to avoid initializing the network if we don't want it
    import network
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if sta_if.isconnected():
        print('wlan already connected')
        print('network config:', sta_if.ifconfig())
        return

    print('Scanning for available Wi-Fi networks...')
    blink(1)
    found_ssids = [tup[0] for tup in sta_if.scan()]
    print(len(found_ssids), 'networks found:')
    for name in found_ssids:
        print('   ', name.decode('latin1'))
    print()
    #
    ssid, password = query_ssid(netdb, found_ssids)
    if not ssid:
        print('Cannot find any known SSID')
        return
    #
    print('SSID %s found in wifi.ini, connecting...' % ssid.decode('latin1'))
    sta_if.connect(ssid, password)
    if timeout > 0 and _wait_for_connection(sta_if, ssid, timeout):
        print('network config:', sta_if.ifconfig())

def query_ssid(netdb, found_ssids):
    for ssid, password in netdb:
        if ssid in found_ssids:
            return ssid, password
    return (None, None)

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

def parse_wifi_ini():
    netdb = []
    try:
        # sta_if.scan() returns bytes, not str: so, it's easier to simply read
        # wifi.ini directly as bytes. Not sure what happens in presence of
        # non-ascii SSIDs :)
        with open('wifi.ini', 'rb') as f:
            for line in f:
                line = line.strip()
                ssid, password = line.split(None, 1)
                netdb.append((ssid, password))
    except OSError:
        pass
    return netdb

def auto_connect(timeout=10):
    netdb = parse_wifi_ini()
    if netdb:
        print('Networks found in wifi.ini:')
        for ssid, _ in netdb:
            print('   ', ssid.decode('latin1'))
        print()
        connect_wifi(netdb, timeout=timeout)
    else:
        print('cannot read wifi.ini, skipping Wi-Fi connection')

# if you want to enable Wi-Fi auto-connect, simply put a wifi.ini: each line
# contains a known ssid and a password, separated by a space:
# $ cat wifi.ini
# ssid1 pwd1
# ssid2 pwd2
# ...
auto_connect(timeout=0)
