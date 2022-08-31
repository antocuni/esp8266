from utime import sleep_ms
from encoder import Encoder  # or from pyb_encoder import Encoder
from wemos_d1 import D1, D2, D6
from machine import Pin
from button import Button

e = Encoder(D2, D1, pin_mode=Pin.PULL_UP)  # optional: add pin_mode=Pin.PULL_UP
lastval = e.value

def on_click(pin):
    print('Button!')

#btn = machine.Pin(D6, machine.Pin.IN, machine.Pin.PULL_UP)
btn = Button(D6, on_click=on_click)


i = 0
print('starting')
while True:
    i += 1
    val = e.value
    if lastval != val:
        lastval = val
        print('newval:', val)
    sleep_ms(300)
    #print('button:', button.value())
