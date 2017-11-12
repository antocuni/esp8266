from machine import ADC, Pin
from wemos_d1 import D0

class Disconnected(Exception):
    pass

class Potentiometer(object):
    """
    Read a potentiometer connected to the ADC.

    Normal wiring:

      - left pin to 3.3v
      - middle pin to A0
      - right pin to GND


    "On header" mode is to mount the potentiometer directly (see
    pot-on-header.jpg). In this mode, the wiring is the following:

      - left pin: RESET (which is at 3.3v)
      - middle pin: A0
      - right pin: D0 (which is put to GND in the __init__)
    """

    def __new__(cls, on_header=False, **kwargs):
        if on_header:
            return PotentiometerOnHeader(**kwargs)
        return object.__new__(cls, **kwargs)

    def __init__(self, on_header):
        assert not on_header
        self.adc = ADC(0)

    def read(self):
        # it seems that 1 <= val <= 1024; adjust it to be 0-based
        val = self.adc.read() - 1
        return round(val/1023.0, 2)


class PotentiometerOnHeader(object):
    """
    Probably because of the impedence of RESET, we ADC is unable to read up to
    1024; on my system, I measured a max reading of 758. Adjust, if needed.
    """

    adc_max = 758.0 # manually measured on my board

    def __init__(self, adc_max=None):
        if adc_max:
            self.adc_max = float(adc_max)
        self.adc = ADC(0)
        self.fake_gnd = Pin(D0, Pin.OUT)
        self.fake_gnd(0)

    def read(self):
        val = self.adc.read() - 1
        if val == 1023:
            # this happens if the potentiometer is not well fixed to the
            # header
            raise Disconnected()
        return round(val/self.adc_max, 2)

