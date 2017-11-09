TTY=/dev/ttyUSB0

# use this to connect to the serial port
# to exit the screen, ctrl-A k
# DO NOT USE ctrl-A d, else the tty stays busy
screen:
	screen -S upython $(TTY) 115200

kill-screen:
	@if screen -ls | grep -q upython; then screen -X -S upython quit; fi

boot: kill-screen
	ampy -p $(TTY) put boot.py
	if [ -f wifi.ini ]; then ampy -p $(TTY) put wifi.ini; fi
