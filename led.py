import Adafruit_BBIO.GPIO as GPIO
import time


def modem_ok_live(): 

	GPIO.setup("P8_10", GPIO.OUT)
	for i in range(1,3):
		GPIO.output("P8_10", GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output("P8_10", GPIO.LOW)
		time.sleep(0.5)


def modem_ok_backfill(): 

	GPIO.setup("P8_10", GPIO.OUT)
	for i in range(1,5):
		GPIO.output("P8_10", GPIO.HIGH)
		time.sleep(0.05)
		GPIO.output("P8_10", GPIO.LOW)
		time.sleep(0.05)
