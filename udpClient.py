import serial
import time
obj = serial.Serial('/dev/ttyS0',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,1)


def sendAt(command):
	"""
	Function to send AT commands
	to GSM Module
	"""
	print command
	code=command + '\r\n'
	obj.write(code)
	time.sleep(0.25)

'''
def gsmInit():
	"""
	Function to wait for initial
	replies from GSM modem
	RDY,+CFUN:1,+CPIN: READY,+CREG: 0,
	+CREG: 2, +CREG: 1
	"""
'''

def checkStatus(success=0,error=0,wait=1,command=0):
	"""
	Function to wait and respond for Replies from modem for each
	AT command sent to it 
	"""
	status = obj.read(100).strip()
	
	
	case = ['RDY','+CFUN: 1','+CPIN: READY',\
			'+CREG: 0','+CREG: 2','+CREG: 1']
	if any(status == s for s in case) or len(status)>20: 	#When powering up,len(status)==31 RDY +CFUN: 1 +CPIN: READY
		if 'at' not in status and command != 'CGATT' and command != 'CREG' and ';' not in status:
			print '\t---->>{{' + status+'}}'
			status = obj.read(100).strip()
	else:
		print '\t((('+status+','+str(len(status))+ ')))'
	print '-----------------------'
	
	cntr=1     					# Timeout in secs
	while len(status)==0 or len(status)==1:			#len(status)=1 when powering up
		
		if status=='>':
			break
		
		if cntr>wait:
			print '\n\tError, Time out, cntr = '+str(cntr)+'\n'
			return 'connError'
		cntr=cntr+1
		status = obj.read(100)
		time.sleep(1)
		#if wait>5:         # If waitin for more than 5 sec display count
		print '\t-'+str(cntr)
	print '-----------------------'
	#print '\t'+status
	if success==0 or error==0: # If no arguments are passed to the function,then wait for any key press
		raw_input()
	else:
		if success not in status:
			print 'success not in status, status = '+status
		elif error in status:
			print 'error in status, status = ' + status
			return 'sendError'
		else:
			print 'AT sent success, status = '+status
			return 'success' # success => AT Command sent

def sendPacket():
	while True:
		sendAt('ate0')
		checkStatus('OK','ERROR')

		sendAt('at+cpin?')
		checkStatus('OK','ERROR')
		
		sendAt('at+csq')
		checkStatus('OK','ERROR')
		
		sendAt('at+creg?')
		checkStatus('OK','ERROR',1,'CREG')
		
		sendAt('at+cgatt?')
		checkStatus('OK','ERROR',1,'CGATT')
		

		sendAt('at+cipshut')
		checkStatus('OK','ERROR')
		
		sendAt('at+cstt="bsnlnet"')
		status=checkStatus('OK','ERROR')
		
		"""if status != None and 'connError' in status:
		pass
		flag='Error'
		else:"""
		sendAt('at+ciicr')
		flag = checkStatus('OK','ERROR',20)
		

		if flag!=None and 'success' in flag:           # Skip the rest if sendError or connError
			sendAt('at+cifsr')
			checkStatus('.','ERROR')
			
			sendAt('at+cipstart="UDP","52.74.106.150","50001"')   # Warning!! Enter correct IP address and Port, 50001 -UDP,50003-TCP
			flag = checkStatus('OK','FAIL')
			print 'flag = '+flag    # flag should be error if reply is CONNECT FAIL
			"""
			msg=obj.read(100).strip()
			while 'CONNECT OK' not in msg:
				if 'CONNECT FAIL' in msg or len(msg)==0:
					break
				print '-----'
				print msg
				print '---'
				msg=obj.read(100).strip()
			"""

			sendAt('at+cipsend')
			checkStatus('>','ERROR')
			
			#sendAt('packet;packet;packet'+'\x1A'+'\x1A')
			obj.write('packet;packet;packet'+'\x1A')
			checkStatus()
			
			sendAt('at+cipclose')
			checkStatus('OK','ERROR')
		else:
			pass
		

sendPacket()