# nokia LCD demo. See this page for wiring:
# https://github.com/mcauser/MicroPython-ESP8266-DHT-Nokia-5110

from machine import Pin, SPI
import pcd8544

spi = SPI(1, baudrate=80000000, polarity=0, phase=0)

cs = Pin(2)
dc = Pin(15)
rst = Pin(0)

bl = Pin(12, Pin.OUT, value=0)
lcd = pcd8544.PCD8544_FRAMEBUF(spi, cs, dc, rst)

def text_inverse(lcd, t, x, y, color):
    w = len(t) * 8
    h = 8
    lcd.fill_rect(x, y, w, h, 1)
    lcd.text(t, x, y, 0)


lcd.text("Hello,", 0, 0, 1)
#lcd.text("World!", 0, 9, 1)
text_inverse(lcd, "World!", 0, 9, 1)
lcd.show()
