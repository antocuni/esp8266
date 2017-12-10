from machine import Pin
import myboard
from button import Button

class MyApp(object):

    def __init__(self):
        self.relay = Pin(myboard.RELAY, Pin.OUT)
        self.led = Pin(myboard.LED, Pin.OUT)
        self.status = False
        self.button = Button(myboard.BUTTON, self.on_click)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        print ("setting status to %s" % value)
        self._status = value
        self.led(not value) # the led is inverted
        self.relay(value)

    def on_click(self, pin):
        # toggle the status
        self.status = not self.status


if __name__ == '__main__':
    app = MyApp()
