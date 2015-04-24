import serial
import time
obj = serial.Serial('/dev/ttyS0',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,1)


def sendAt(command,success=0,error=0,wait=1):
	"""
	Function to send AT commands
	to GSM Module
	"""
	print '{0:20}'.format(command),
	code=command + '\r\n'
	obj.write(code)
	time.sleep(0.25)
	
	status=checkStatus(success,error,wait)
	return status

def checkStatus(success=0,error=0,wait=1):
	"""
	Function to wait and respond for Replies from modem for each
	AT command sent to it 
	"""
	status = obj.read(100).strip()
	
	
	cntr=1     					# Timeout in secs
	while len(status)==0:			
		
		if cntr>wait:
			print '\n\tError, Time out, cntr = '+str(cntr)+'\n'
			return 'connError'
		cntr=cntr+1
		
		status = obj.read(100)
		time.sleep(1)
		if wait>1:         # If waitin for more than 5 sec display count
			print '\n\t'+str(cntr)

	
	#print '\t((('+status+')))'
	
	"""string = [s.split(' ').strip() for s in status]"""

	string=status.split('\n')
	string = ''.join(string)
	string = string.replace('\r',',')
	string = string.replace(',,','; ')

	if success==0 or error==0: # If no arguments are passed to the function,then wait for any key press
		raw_input()
	else:
		if success in status:
			#print '\t\t',
			print '{0:20} ==> {1:50}'.format('success',string)
			return 'success'  # success => AT Command sent
		elif error in status:
			print '{0:20} ==> {1:50}'.format('Error',string)
			return 'sendError'
		else:
			print '{0:20} ==> {1:50}'.format('Other',string)
			return 'other'

def sendPacket():
	while True:
		sendAt('ate0','OK','ERROR')
		sendAt('at+cpin?','OK','ERROR')
		sendAt('at+csq','OK','ERROR')
		sendAt('at+creg?','OK','ERROR')
		sendAt('at+cgatt?','OK','ERROR')
		sendAt('at+cipshut','OK','ERROR')
		status=sendAt('at+cstt="bsnlnet"','OK','ERROR')
		
		if 'connError' in status:
			flag='Error'
			pass
		else:
			flag = sendAt('at+ciicr','OK','ERROR',20)
		

		if 'success' in flag:           # Skip the rest if sendError or connError
			sendAt('at+cifsr','.','ERROR')
			flag = sendAt('at+cipstart="UDP","52.74.106.150","50001"','OK','ERROR')   # Warning!! Enter correct IP address and Port, 50001 -UDP,50003-TCP
			#print 'flag = '+flag    # flag should be error if reply is CONNECT FAIL
			sendAt('at+cipsend','>','ERROR')
			obj.write('packet;packet;packet'+'\x1A')
			checkStatus('OK','ERROR')
			sendAt('at+cipclose','OK','ERROR')
			
		else:
			sendAt('at+cipclose','OK','ERROR')
			

sendPacket()