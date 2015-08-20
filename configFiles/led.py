import RPi.GPIO as g
import time

gsm = 11
plc = 13
send = 35
at = 15
code = 37

def blink(pin):
	g.setup(pin,g.OUT)
	g.output(pin,1)
	time.sleep(0.5)
	g.output(pin,0)
	time.sleep(0.5)


g.setmode(g.BOARD)
while True:
	blink(gsm)
	blink(plc)
	blink(send)
	blink(at)
	blink(code)
g.cleanup()

