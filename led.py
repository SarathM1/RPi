import RPi.GPIO as gpio
from RPi.GPIO import OUT as out
from RPi.GPIO import LOW as low 
from RPi.GPIO import HIGH as high 

import time
import threading, Queue
import random

class hwThread(threading.Thread):
    
    def __init__(self, pin):
        super(hwThread, self).__init__()
        self.stoprequest = threading.Event()

        self.pin = pin

    def run(self):
        
        while not self.stoprequest.isSet():
            if self.pin == pin["plc_ok"]:
            	hw(pin["plc_ok"],plc_ok)
            else:
            	hw(pin["modem_ok"],modem_ok)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(hwThread, self).join(timeout)

class debugThread(threading.Thread):
    
    def __init__(self, pin, q):
        super(debugThread, self).__init__()
        self.q = q
        self.pin = pin
        self.stoprequest = threading.Event()

    def run(self):
        
        while not self.stoprequest.isSet():
        	print "\n\twaiting for Queue, PIN: "+str(self.pin)+"\n"
        	status = self.q.get()
        	print "Done waiting: "+str(status)
        	
        	if status == "off":
        		off(self.pin)

    		elif status == "on":
    			blink_led(self.pin,0.1)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(debugThread, self).join(timeout)

class commStatusThread(threading.Thread):
    
    def __init__(self, pin, q):
        super(commStatusThread, self).__init__()
        self.q = q
        self.pin = pin
        self.stoprequest = threading.Event()

    def run(self):
        
        while not self.stoprequest.isSet():
        	status = self.q.get()
        	
        	if status == "off":
        		off(self.pin)

    		elif status == "live_send_ok":
    			blink_led(self.pin,1)

    		elif status == "backfill_send_ok":
    			blink_led(self.pin,0.1)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(commStatusThread, self).join(timeout)

def hw(pin,status):
	"""
	To check state of PLC and GSM
	pin - pin # of device
	"""
	if status == "off" :
		off(pin)
	elif status == "working":
		on(pin)
	elif status == "usb_disconnected":
		blink_led(pin,1)
	elif status == "comm_error":
		blink_led(pin,0.1)



def led_init():
	gpio.setmode(gpio.BOARD)
	gpio.setwarnings(False)


	for x in pin :
		gpio.setup(pin[x], out)
		gpio.output(pin[x], low)

def on(pin):
	gpio.output(pin, high)

def off(pin):
	gpio.output(pin, low)

def blink_led(pin,sec):
	"""
	To blink and led connected to 'pin'
	with intervel 'sec' seconds
	""" 
	on(pin)
	time.sleep(sec)
	off(pin)
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

code	 		= Queue.Queue()
code.put("off")

led_init()

plc_th = hwThread(pin["plc_ok"])
gsm_th = hwThread(pin["modem_ok"])
at_th = debugThread(pin["at"],at)
code_th = debugThread(pin["code"],code)
commStatus_th = commStatusThread(pin["comm_status"],comm_status)

threads = []
threads.append(plc_th)
threads.append(gsm_th)
threads.append(at_th)
threads.append(code_th)
threads.append(commStatus_th)

for each_thread in threads:
	each_thread.start()		# Starting all threads here



