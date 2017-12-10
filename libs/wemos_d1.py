# pin numbers
# http://micropython-on-wemos-d1-mini.readthedocs.io/en/latest/setup.html
# https://forum.micropython.org/viewtopic.php?t=2503

D0 = 16 # wake
D5 = 14 # sck
D6 = 12 # miso
D7 = 13 # mosi
D8 = 15 # cs    PULL-DOWN 10k

D4 = 2 # boot   PULL-UP   10k
D3 = 0 # flash  PULL-UP   10k
D2 = 4 # sda
D1 = 5 # scl
RX = 3 # rx
TX = 1 # tx

# note: D4 is also used to control the builtin blue led, but it's reversed
# (when D4 is 1, the led is off)
LED = D4
