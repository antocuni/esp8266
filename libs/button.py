import machine

class Button(object):

    def __init__(self, pin, on_click=None):
        self.pin = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.on_click)
        if on_click:
            self.on_click = on_click

    def on_click(self, pin):
        pass


if __name__ == '__main__':
    # this demo was tested on sonoff
    from myboard import BUTTON
    class MyButton(Button):
        def on_click(self, pin):
            print('click')

    button = MyButton(BUTTON)
