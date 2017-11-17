TTY=/dev/ttyUSB0

boot: kill-screen
	ampy -p $(TTY) put boot.py
	#if [ -f wifi.ini ]; then ampy -p $(TTY) put wifi.ini; fi

libs: kill-screen
	#ampy -p $(TTY) mkdir libs
	ampy -p $(TTY) put libs/wemos_d1.py libs/wemos_d1.py
	ampy -p $(TTY) put libs/potentiometer.py libs/potentiometer.py

standing_wave: kill-screen
	ampy -p $(TTY) put standing_wave/main.py main.py

analog: kill-screen
	ampy -p $(TTY) put analog/main.py main.py

potmotor: kill-screen
	ampy -p $(TTY) put potmotor/main.py main.py

kill-screen:
	@if screen -ls | grep -q upython; then screen -X -S upython quit; fi

# use this to connect to the serial port
# to exit the screen, ctrl-A k
# DO NOT USE ctrl-A d, else the tty stays busy
screen:
	screen -S upython $(TTY) 115200

