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
	
	def __init__(self,q,stopEvent,name="plc_ok_th"):
		#super(plc_ok_th, self).__init__()
		self.stopEvent = stopEvent
		self.sleepPeriod = 0.001
		self.q = q
		threading.Thread.__init__(self,name=name)
	def run(self):
		print "\n\t THREAD %s STARTS !!" %(self.getName(),)
		while not self.stopEvent.isSet():
			
			try:
				status = self.q.get(True,2)		# To make queue non-blocking
			except Empty as e:
				pass
			with self.q.mutex:							# TRY UNCOMMENTING, IF QUEUE SIZE INCREASES
				self.q.queue.clear()  # Flushig Queue
				
			if self.q.qsize()>1:
				print "QUE SIZE = "+ str(self.q.qsize())
			
			plc_check(pin["plc_ok"],status)
			self.stopEvent.wait(self.sleepPeriod)
		print "\n\t THREAD %s ENDS !!" %(self.getName(),)

	def join(self,timeout = None):
		self.stopEvent.set()
		threading.Thread.join(self,timeout)

class modem_ok_th(threading.Thread):
	
	def __init__(self,q,stopEvent,name = "modem_ok_th"):
		#super(modem_ok_th, self).__init__()
		self.stopEvent = stopEvent
		self.sleepPeriod = 0.001
		self.q = q
		threading.Thread.__init__(self,name=name)

	def run(self):
		print "\n\t THREAD %s STARTS !!" %(self.getName(),)
		while not self.stopEvent.isSet():
			status = self.q.get()

			with self.q.mutex:
				self.q.queue.clear()  # Flushig Queue
				
			if self.q.qsize()>1:
				print "QUE SIZE = %d " %(self.q.qsize(), )
			
			modem_check(pin["modem_ok"],status)
			self.stopEvent.wait(self.sleepPeriod)
		print "\n\t THREAD %s ENDS !!" %(self.getName(),)

	def join(self,timeout = None):
		self.stopEvent.set()
		threading.Thread.join(self,timeout)

def plc_check(pin_no,status):
	"""
	To check state of PLC 
	pin_no - pin # of device
	"""
	if status == "off" :
		off(pin_no)

	elif status == "working":
		on(pin_no)

	elif status == "usb_disconnected":
		blink_fast(pin_no)
		
	elif status == "comm_error":
		led_breathe(pin_no)

	else:
		print "Unexpected Value Pushed to Queue!!"
	
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
		blink_fast(pin_no)
	elif status == "comm_error":
		led_breathe(pin_no)
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

def blink_fast(pin_no,sec = 0.1):
	"""
	To blink and led connected to 'pin'
	with intervel 'sec' seconds
	""" 
	try:
		
		for i in range(5):
			on(pin_no)
			time.sleep(sec)
			off(pin_no)
			time.sleep(sec)

	except Exception, e:
		print "blink_fast: " + str(e)

def cleanup():
	gpio.cleanup()

def blink_slow(pin_no,sec = 0.1):
	"""
	To blink and led connected to 'pin'
	with intervel 'sec' seconds
	""" 
	try:
		on(pin_no)
		time.sleep(sec)
		off(pin_no)
			
	except Exception, e:
		print "blink_slow: " + str(e)

def led_breathe(pin_no):
	"""
	Fn to vary the duty cycle to   
	dim/brighten the leds
	"""
	try:
		
		pwm = PWM(pin_no,100) 	# create object for PWM on port pin_no at 100 Hertz
		pwm.start(0)			# start led on 0 percent duty cycle (off)
		for i in range(101):
			pwm.ChangeDutyCycle(i) # Increase duty cycle from 0% to 100% (step by 1) 
			time.sleep(0.01)
		for i in range(100,-1,-1):
			pwm.ChangeDutyCycle(i)	# Decrease duty cycle from 0% to 100% (step by 1)
			time.sleep(0.01)
		time.sleep(1)
		pwm.stop()

	except Exception, e:
		print "led_breathe: " + str(e)
					# stop the PWM output 

pin = {}

pin["comm_status"] 	= 35
pin["modem_ok"] 	= 11
pin["plc_ok"]		= 13
pin["at"] 		 	= 15
pin["code"]	 		= 37

led_init()





