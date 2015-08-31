import RPi.GPIO as gpio
from RPi.GPIO import OUT as out
from RPi.GPIO import LOW as low 
from RPi.GPIO import HIGH as high 
from RPi.GPIO import PWM

import time
import threading
import random
from Queue import Empty

class plc_ok_th(threading.Thread):
	
	def __init__(self,q):
		super(plc_ok_th, self).__init__()
		self.q = q

	def run(self):
		while True:
			
			try:
				status = self.q.get(True,2)		# To make queue non-blocking
			except Empty as e:
				pass
			with self.q.mutex:							# TRY UNCOMMENTING, IF QUEUE SIZE INCREASES
				self.q.queue.clear()  # Flushig Queue
				
			if self.q.qsize()>1:
				print "QUE SIZE = "+ str(self.q.qsize())
			
			plc_check(pin["plc_ok"],status)

class modem_ok_th(threading.Thread):
	
	def __init__(self,q):
		super(modem_ok_th, self).__init__()
		self.q = q

	def run(self):
		while True:
			status = self.q.get()

			with self.q.mutex:
				self.q.queue.clear()  # Flushig Queue
				
			#print "QUE SIZE = "+ str(self.q.qsize())
			modem_check(pin["modem_ok"],status)

def plc_check(pin_no,status):
	"""
	To check state of PLC 
	pin_no - pin # of device
	"""
	if status == "off" :
		if pin["plc_ok"] == pin_no:
			print "\n\tPLC OFF!!"
		off(pin_no)
	elif status == "working":
		#if pin["plc_ok"] == pin_no:
			#print "\n\tPLC WORKING!!"
		on(pin_no)
	elif status == "usb_disconnected":
		if pin["plc_ok"] == pin_no:
			print "\n\tPLC USB DISCONNECTED!!"
		blink_led(pin_no,1)
	elif status == "comm_error":
		if pin["plc_ok"] == pin_no:
			print "\n\tPLC COMMUNICATION ERROR!!"
		blink_led(pin_no,0.1)
	else:
		if pin["plc_ok"] == pin_no:
			print "Error!!"
	#time.sleep(0.01)							# DANGEROUS !! MAY CAUSE ERRROR

def modem_check(pin_no,status):
	"""
	To check state of PLC and GSM
	pin_no - pin # of device
	"""
	if status == "off" :
		off(pin_no)
	elif status == "working":
		on(pin_no)
	elif status == "usb_disconnected":
		blink_led(pin_no,1)
	elif status == "\n\tCOMMUNICATION ERROR!!":
		blink_led(pin_no,0.1)
	else:
		pass	

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
	on(pin_no)
	time.sleep(sec)
	off(pin_no)

def led_breathe():
	obj = PWM(pin["at"],100)
	obj.start(0)
	while True:
		for i in range(101):
			obj.ChangeDutyCycle(i)
			time.sleep(0.03)
		for i in range(100,-1,-1):
			obj.ChangeDutyCycle(i)
			time.sleep(0.03)
		time.sleep(1)
pin = {}

pin["comm_status"] 	= 35
pin["modem_ok"] 	= 11
pin["plc_ok"]		= 13
pin["at"] 		 	= 15
pin["code"]	 		= 37

led_init()
led_breathe()




