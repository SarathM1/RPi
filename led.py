import Adafruit_BBIO.GPIO as GPIO
import time

com 	 = "P8_10"
modem 	 = "P8_12"

GPIO.setup(com , GPIO.OUT)
GPIO.setup(modem , GPIO.OUT)

def comm_status_live(): 

	for i in range(1,3):
		GPIO.output(com, GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(com, GPIO.LOW)
		time.sleep(0.5)


def comm_status_backfill(): 

	for i in range(1,5):
		GPIO.output(com, GPIO.HIGH)
		time.sleep(0.05)
		GPIO.output(com, GPIO.LOW)
		time.sleep(0.05)

def modem_ok(arg):
	
	if arg == 1 :
		GPIO.output(modem , GPIO.HIGH)
	else :
		GPIO.output(modem, GPIO.HIGH)
		time.sleep(1)
		GPIO.output(modem, GPIO.LOW)
		time.sleep(3)


