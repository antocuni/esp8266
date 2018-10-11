from utime import sleep_ms
from encoder import Encoder  # or from pyb_encoder import Encoder
from wemos_d1 import D1, D2
from machine import Pin

e = Encoder(D2, D1, pin_mode=Pin.PULL_UP)  # optional: add pin_mode=Pin.PULL_UP
lastval = e.value

i = 0
while True:
    i += 1
    val = e.value
    if lastval != val:
        lastpos = val
        print(val)
    sleep_ms(300)
    
