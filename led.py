import RPi.GPIO as gpio
from RPi.GPIO import OUT as out
from RPi.GPIO import LOW as low 
from RPi.GPIO import HIGH as high 

import time
import threading
import random

class plc_ok_th(threading.Thread):
	
	def __init__(self,q):
		super(plc_ok_th, self).__init__()
		self.q = q

	def run(self):
		while True:
			status = self.q.get()

			with self.q.mutex:
				self.q.queue.clear()  # Flushig Queue
				
			self.q.put(status)
			#print "QUE SIZE = "+ str(self.q.qsize())
			hw(pin["plc_ok"],status)

class modem_ok_th(threading.Thread):
	
	def __init__(self,q):
		super(modem_ok_th, self).__init__()
		self.q = q

	def run(self):
		while True:
			status = self.q.get()

			with self.q.mutex:
				self.q.queue.clear()  # Flushig Queue
				
			self.q.put(status)
			#print "QUE SIZE = "+ str(self.q.qsize())
			hw(pin["modem_ok"],status)

def hw(pin_no,status):
	"""
	To check state of PLC and GSM
	pin_no - pin # of device
	"""
	if status == "off" :
		if pin["modem_ok"] == pin_no:
			print "\n\tOFF!!"
		off(pin_no)
	elif status == "working":
		if pin["modem_ok"] == pin_no:
			print "\n\tWORKING!!"
		on(pin_no)
	elif status == "usb_disconnected":
		if pin["modem_ok"] == pin_no:
			print "\n\tUSB DISCONNECTED!!"
		blink_led(pin_no,1)
	elif status == "\n\tCOMMUNICATION ERROR!!":
		if pin["modem_ok"] == pin_no:
			print "\ncomm_error"
		blink_led(pin_no,0.1)
	else:
		if pin["modem_ok"] == pin_no:
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





