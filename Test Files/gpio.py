#!/usr/bin/env python 
import Adafruit_BBIO.GPIO as GPIO
import time

GPIO.cleanup()
 
while True:
	GPIO.setup("P8_10", GPIO.OUT)
	GPIO.output("P8_10", GPIO.HIGH)
	time.sleep(1)
	GPIO.output("P8_10", GPIO.LOW)
	time.sleep(1)
