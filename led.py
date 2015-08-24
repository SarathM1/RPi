import RPi.GPIO as gpio
from RPi.GPIO import out as out
from RPi.GPIO import LOW as low 
from RPi.GPIO import HIGH as high 
import time

pin = {}

pin["comm_status"] 	= 35
pin["modem_ok"] 	= 11
pin["plc_ok"]		= 13
pin["at"] 		 	= 15
pin["code"]	 		= 37

comm_status 	= "off"
modem_ok 	 	= "off"
plc_ok		 	= "off"
at 		 		= "off"
code	 		= "off"

gpio.setmode(gpio.BOARD)
gpio.setwarnings(False)


for x in pin :
	gpio.setup(pin[x], out)
	gpio.output(pin[x], low)

def on(pin):
	gpio.output(code, high)

def off(pin):
	gpio.output(code, low)

def blink_led(pin): 
	on(pin)
	time.sleep(0.05)
	off(pin)
	time.sleep(0.05)



