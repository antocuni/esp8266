# instructions to flash:
# http://www.instructables.com/id/How-to-Flash-MicroPython-Firmware-on-a-ESP8266-Bas/

# NOTE: according to this thread, depending on your "flash_id", you might have
# to flash the firmware using the "-fm dout" option:
# https://forum.micropython.org/viewtopic.php?f=16&t=3777
#
#   esptool.py --port /dev/ttyUSB0 erase_flash
#   esptool.py --port /dev/ttyUSB0 write_flash -fs 1MB -fm dout 0x0 esp8266-20170823-v1.9.2.bin

RELAY = 12
LED = 13   # 0 to turn the led on, 1 to turn it off
BUTTON = 0
GPIO14 = 14
