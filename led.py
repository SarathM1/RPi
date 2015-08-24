import RPi.GPIO as gpio
from RPi.GPIO import OUT as out
from RPi.GPIO import LOW as low 
from RPi.GPIO import HIGH as high 

import time
import threading, Queue
import random

class hwThread(threading.Thread):
	
	def __init__(self):
		super(hwThread, self).__init__()
		self.stoprequest = threading.Event()

	def run(self):
		print "\n\tPLC_OK: "+str(plc_ok)+", stoprequest: "+str(self.stoprequest.isSet())	
		while not self.stoprequest.isSet():
			print "\n\tPLC_OK: "+str(plc_ok)+", stoprequest: "+str(self.stoprequest.isSet())	
			time.sleep(1)  # debugging
			hw(pin["plc_ok"],plc_ok)
			hw(pin["modem_ok"],modem_ok)

	def join(self, timeout=None):
		self.stoprequest.set()
		super(hwThread, self).join(timeout)

def hw(pin_no,status):
	"""
	To check state of PLC and GSM
	pin_no - pin # of device
	"""
	if status == "off" :
		if pin["plc_ok"] == pin_no:
			print "\n\tOFF!!"
		off(pin_no)
	elif status == "working":
		if pin["plc_ok"] == pin_no:
			print "\n\tWORKING!!"
		blink_led(pin_no,1)
	elif status == "usb_disconnected":
		if pin["plc_ok"] == pin_no:
			print "\n\tUSB DISCONNECTED!!"
		blink_led(pin_no,1)
	elif status == "\n\tCOMMUNICATION ERROR!!":
		if pin["plc_ok"] == pin_no:
			print "\ncomm_error"
		blink_led(pin_no,0.1)
	else:
		if pin["plc_ok"] == pin_no:
			print "Error!!"
	time.sleep(1)


def led_init():
	gpio.setmode(gpio.BOARD)
	gpio.setwarnings(False)


	for x in pin :
		gpio.setup(pin[x], out)
		gpio.output(pin[x], low)

def on(pin_no):
	gpio.output(pin_no, high)

def off(pin_no):
	gpio.output(pin_no, low)

def blink_led(pin_no,sec):
	"""
	To blink and led connected to 'pin'
	with intervel 'sec' seconds
	""" 
	on(pin_no)
	time.sleep(sec)
	off(pin_no)
	time.sleep(sec)

#if __name__ == '__main__':
pin = {}

pin["comm_status"] 	= 35
pin["modem_ok"] 	= 11
pin["plc_ok"]		= 13
pin["at"] 		 	= 15
pin["code"]	 		= 37

comm_status 	= Queue.Queue()
comm_status.put("off")

modem_ok 	 	= "off"
plc_ok		 	= "off"

at 		 		= Queue.Queue()
at.put("off")


led_init()


#plc_th = hwThread(pin["plc_ok"])




