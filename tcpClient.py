import serial
import time
obj = serial.Serial('/dev/ttyS0',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,1)

def at(command):
	print command
	code=command + '\r\n'
	obj.write(code)
	time.sleep(0.25)
def checkStatus(success=0,error=0):
	status = obj.read(100).strip()
	x=1
	"""if not status:
			return 'gsmModuleOffError'   # If gsm modem doesn't reply
		else:
			print 'none'"""
	while len(status)==0:
		if x>20:
			print '\n\tError, Connection time out, x = '+str(x)+'\n'
			return 'connError'
		x=x+1
		status = obj.read(100)
		time.sleep(1)
		print '\t'+str(x)

	print '\t'+status
	if success==0 or error==0:
		raw_input()
	else:
		while success not in status:
			if error in status:
				return 'sendError'
	return 'success' # AT Command sent

def send():
	while True:
		at('ate0')
		checkStatus('OK','ERROR')

		at('at+cpin?')
		checkStatus('OK','ERROR')
		
		at('at+csq')
		checkStatus('OK','ERROR')
		
		at('at+creg?')
		checkStatus('OK','ERROR')
		
		at('at+cgatt?')
		checkStatus('OK','ERROR')
		
		at('at+cipshut')
		checkStatus('OK','ERROR')
		
		at('at+cstt="bsnlnet"')
		checkStatus('OK','ERROR')
		
		at('at+ciicr')
		flag = checkStatus('OK','ERROR')
		
		if 'success' in flag:           # Skip the rest if sendError or connError
			at('at+cifsr')
			checkStatus('.','ERROR')
			
			at('at+cipstart="TCP","52.74.106.150","50003"')
			flag = checkStatus('OK','FAIL')
			print 'flag = '+flag    # flag should be error if reply is CONNECT FAIL
			msg=obj.read(100).strip()
			
			while 'CONNECT OK' not in msg:
				if 'CONNECT FAIL' in msg or len(msg)==0:
					break
				print '-----'
				print msg
				print '---'
				msg=obj.read(100).strip()
			
			at('at+cipsend')
			checkStatus('>','ERROR')
			
			#at('packet;packet;packet'+'\x1A'+'\x1A')
			obj.write('packet;packet;packet'+'\x1A')
			checkStatus()
			"""
			at('at+cipclose')
			checkStatus('OK','ERROR')"""
		else:
			pass
		

send()