from machine import Pin, PWM
from myboard import LED

def blink(freq, pin=LED):
    led = Pin(pin)
    pwm = PWM(led)
    if freq == 0:
        pwm.deinit()
        led(1) # turn it off
        return
    pwm.duty(512) # 50% on, 50% off
    pwm.freq(freq)
