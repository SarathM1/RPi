import RPi.GPIO as GPIO
import time


comm_status_pin = 35
modem_ok_pin 	 = 11
plc_ok_pin		 = 13
at_pin 		 = 15
code_pin	 = 37

comm_status = 0
modem_ok_status 	 = 0
plc_ok_status		 = 0
at_status 		 = 0
code_status	 = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(comm_status_pin , GPIO.OUT)
GPIO.setup(modem_ok_pin , GPIO.OUT)
GPIO.setup(plc_ok_pin , GPIO.OUT)
GPIO.setup(at_pin , GPIO.OUT)
GPIO.setup(code_pin , GPIO.OUT)

GPIO.output(comm_status_pin , GPIO.LOW)
GPIO.output(modem_ok_pin , GPIO.LOW)
GPIO.output(plc_ok_pin , GPIO.LOW)
GPIO.output(at_pin , GPIO.LOW)
GPIO.output(code_pin , GPIO.LOW)

def comm_status(arg): 
	if arg == "live":
		GPIO.output(comm_status_pin, GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(comm_status_pin, GPIO.LOW)
		time.sleep(0.5)
	else:

		for i in range(1,5):
			GPIO.output(comm_status_pin, GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(comm_status_pin, GPIO.LOW)
			time.sleep(0.05)

def modem_ok(arg):
	
	if arg == "working" :
		GPIO.output(modem_ok_pin , GPIO.HIGH)
	elif arg == "timeout" :
		for i in range(1,5):
			GPIO.output(modem_ok_pin, GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(modem_ok_pin, GPIO.LOW)
			time.sleep(0.05)
	else :
		GPIO.output(modem_ok_pin, GPIO.LOW)
		time.sleep(1)
		GPIO.output(modem_ok_pin, GPIO.HIGH)
		time.sleep(3)
		

def plc_ok(arg):
	
	if arg == "working" :
		GPIO.output(plc_ok_pin , GPIO.HIGH)
	elif arg == "plc_disconnected" :
		for i in range(1,5):
			GPIO.output(plc_ok_pin, GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(plc_ok_pin, GPIO.LOW)
			time.sleep(0.05)
	else :
		GPIO.output(plc_ok_pin, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(plc_ok_pin, GPIO.LOW)
		time.sleep(3)

def at_status(arg):
	if arg == "live" :
		GPIO.output(at_pin, GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(at_pin, GPIO.LOW)
		time.sleep(0.1)
	else:
		GPIO.output(at_pin, GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(at_pin, GPIO.LOW)
		time.sleep(0.5)

def code_status():
	GPIO.output(code_pin, GPIO.HIGH)

