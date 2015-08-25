import RPi.GPIO as gpio
from RPi.GPIO import OUT as out
from RPi.GPIO import LOW as low 
from RPi.GPIO import HIGH as high 

import time
import threading
import random

class hwThread(threading.Thread):
	
	def __init__(self,q):
		super(hwThread, self).__init__()
		self.q = q
		self.q.put("off")

	def run(self):
		while True:
			status = self.q.get()

			with self.q.mutex:
				self.q.queue.clear()
				
			self.q.put(status)
			print "QUE SIZE = "+ str(self.q.qsize())
			#print 'plc_ok STATUS: '+status
			hw(pin["plc_ok"],status)
	
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

pin = {}

pin["comm_status"] 	= 35
pin["modem_ok"] 	= 11
pin["plc_ok"]		= 13
pin["at"] 		 	= 15
pin["code"]	 		= 37

led_init()





