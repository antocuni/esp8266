"""
Control motor speed (via NPN transistor+PWM) using the potentiometer
"""

import time
from machine import Pin, PWM
from wemos_d1 import D3
from potentiometer import Potentiometer, Disconnected

class Motor(object):

    # I'm using a 12v voltage generator, but I want max 9v at the motor
    MAX_PWM = 0.75
    _MAX_DUTY = 1024 * MAX_PWM

    def __init__(self, p):
        self.pin = Pin(p, Pin.OUT)
        self.pwm = PWM(self.pin, freq=1000)

    def __enter__(self):
        return self

    def __exit__(self, etype, evalue, tb):
        self.pwm.duty(0)
        self.pin(0)

    def go(self, duty):
        duty = int(duty * 1024 * self.MAX_PWM)
        assert duty < self._MAX_DUTY
        print(duty)
        self.pwm.duty(duty)

motor = Motor(D3)

def main():
    pot = Potentiometer(on_header=True)
    with motor:
        while True:
            time.sleep(0.1)
            value = pot.read()
            print('value = %f' % value)
            motor.go(value)

#main()
