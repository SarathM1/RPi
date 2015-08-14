import Adafruit_BBIO.GPIO as GPIO
import time

com 	 = "P8_10"
modem 	 = "P8_12"
plc		 = "P8_14"
at 		 = "P8_16"
code	 = "P8_18"

GPIO.setup(com , GPIO.OUT)
GPIO.setup(modem , GPIO.OUT)
GPIO.setup(plc , GPIO.OUT)
GPIO.setup(at , GPIO.OUT)
GPIO.setup(code , GPIO.OUT)

def comm_status(arg): 
	if arg == "live":
		GPIO.output(com, GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(com, GPIO.LOW)
		time.sleep(0.5)
	else:

		for i in range(1,5):
			GPIO.output(com, GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(com, GPIO.LOW)
			time.sleep(0.05)

def modem_ok(arg):
	
	if arg == "working" :
		GPIO.output(modem , GPIO.HIGH)
	elif arg == "timeout" :
		for i in range(1,5):
			GPIO.output(modem, GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(modem, GPIO.LOW)
			time.sleep(0.05)
	else :
		GPIO.output(modem, GPIO.LOW)
		time.sleep(3)
		GPIO.output(modem, GPIO.HIGH)
		time.sleep(1)
		

def plc_ok(arg):
	
	if arg == "working" :
		GPIO.output(plc , GPIO.HIGH)
	elif arg == "plc_disconnected" :
		for i in range(1,5):
			GPIO.output(plc, GPIO.HIGH)
			time.sleep(0.05)
			GPIO.output(plc, GPIO.LOW)
			time.sleep(0.05)
	else :
		GPIO.output(plc, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(plc, GPIO.LOW)
		time.sleep(3)

def at_status():
	GPIO.output(at, GPIO.HIGH)
	time.sleep(0.05)
	GPIO.output(at, GPIO.LOW)
	time.sleep(0.05)

def code_status():
	GPIO.output(code, GPIO.HIGH)





