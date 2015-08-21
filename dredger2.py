
#!/usr/bin/python
import serial
import time
import threading, Queue
from backfill import database_backup
from errorFile import errorHandlerMain      # Import from local file errorFile
from errorFile import errorHandlerGsm      # Import from local file errorFile
from errorFile import errorHandlerTimeout      # Import from local file errorFile
from errorFile import errorHandlerUnknown      # Import from local file errorFile

import os
import myLogger as log
import minimalmodbus
import led
"""
Install Library Minimalmodbus 0.6,
there is error in using MODE_ASCII in python 3 for Minimalmodbus 0.5 library

Source: http://sourceforge.net/projects/minimalmodbus/?source=typ_redirect
Commands:
				cd /home/wa/Music/MinimalModbus-0.6
				sudo python3 setup.py install
"""


def dummyPacket():
	cap=['Close','Open']
	status=['Off','On']
	arg={}

	arg['dredger_name']         = 'dredger2'
	arg['time']                 = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
	arg['storage_tank_level']   = 0
	arg['storage_tank_cap']     = cap[0]
	arg['service_tank_level']   = 0
	arg['service_tank_cap']     = cap[0]
	arg['flowmeter_1_in']       = 0
	arg['flowmeter_1_out']      = 0
	arg['engine_1_status']      = status[0]
	arg['flowmeter_2_in']       = 0
	arg['flowmeter_2_out']      = 0
	arg['engine_2_status']      = status[0]


	return arg



class plc():
	def __init__(self):
		try:
			self.instrument = minimalmodbus.Instrument('/dev/plc',1)
			self.instrument.serial.baudrate = 9600
			self.instrument.serial.bytesize = 7
			self.instrument.serial.parity = serial.PARITY_EVEN
			self.instrument.serial.stopbits = 1
			self.instrument.serial.timeout = 0.1
			self.instrument.mode = minimalmodbus.MODE_ASCII
			errMain.clearBit('plcUsb')
			led.plc_ok_status = 1
		except serial.SerialException:
			errMain.setBit('plcUsb')
			liveLog.error("PLC: CANNOT OPEN PORT")
			led.plc_ok_status = 2 
			print '\n\t\tPLC: CANNOT OPEN PORT!!'

		except Exception as e:
			liveLog.error("PLC: CANNOT OPEN PORT")
			print '\nplc_init: '+str(e)+'\n'
			errMain.setBit('plcUsb')                               # Error code for logging
			led.plc_ok_status = 2

	def readData(self):
		cap=['Close','Open']
		status=['Off','On']
		arg={}

		try:

			if errMain.checkBit('plcUsb'):       # If PLC is disconnected
				print '\n\t\tERROR: PLC DISCONNECTED !!\
					\n\r\t\tRETURNING DUMMY PACKET\n\n'
				arg = dummyPacket()

			else:

				arg['dredger_name']         = 'dredger2'
				arg['time']                 = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
				arg['storage_tank_level']   = self.instrument.read_register(4096) #404097 is 4097-1 in python
				arg['storage_tank_cap']     = cap[self.instrument.read_register(4104)]
				arg['service_tank_level']   = self.instrument.read_register(4097)
				arg['service_tank_cap']     = cap[self.instrument.read_register(4105)]
				arg['flowmeter_1_in']       = self.instrument.read_register(4098)
				arg['flowmeter_1_out']      = self.instrument.read_register(4100)
				arg['engine_1_status']      = status[self.instrument.read_register(4106)]
				arg['flowmeter_2_in']       = self.instrument.read_register(4103)
				arg['flowmeter_2_out']      = self.instrument.read_register(4101)
				arg['engine_2_status']      = status[self.instrument.read_register(4107)]

				debugLog.info("Data read from PLC")
				print "\n\t\tDATA READ FROM PLC!!\n\n"
				errMain.clearBit('plcComm')
				led.plc_ok_status = 1		# PLC is working properly

		except Exception as e:
				liveLog.error("PLC: Communication Error")
				print 'PLC_read_data: ',str(e)
				errMain.setBit('plcComm')
				arg = dummyPacket()
				led.plc_ok_status = 3		# Communication Error with PLC
				

		return arg

class Sim900():
	def __init__ (self):
		self.status=0
		try:
			#self.obj = serial.Serial('/dev/ttyS0', 9600, timeout=1)
			self.obj = serial.Serial('/dev/gsmModem', 9600, timeout=1)
			errMain.clearBit('gsmUsb')
			led.modem_ok_status = 1		# GSM modem working properly

		except serial.SerialException:
			errMain.setBit('gsmUsb')
			liveLog.error("GSM: CANNOT OPEN PORT")
			print '\n\t\tGSM: CANNOT OPEN PORT!!'
			led.modem_ok_status = 2		# GSM disconnected from USB

		except Exception as e:
			errMain.setBit('gsmUsb')
			liveLog.error("GSM: CANNOT OPEN PORT")
			led_q.put((,,,,)) modem_ok("gsm_disconnected")
			print 'Sim900, __init__:- '+str(e)
			led.modem_ok_status = 2		# GSM disconnected from USB

		self.db=database_backup()
	
	def hotPlug(self,loggerMsg="USB disconnected"):
		print loggerMsg
		try:
			#self.obj = serial.Serial('/dev/ttyS0', 9600, timeout=1)
			self.obj = serial.Serial('/dev/gsmModem', 9600, timeout=1)
			led.modem_ok_status = 1			# GSM Connection OK via USB

		except Exception as e:
			led.modem_ok_status = 1
			print 'hotPlug():',e
		debugLog.error(loggerMsg)

	def sendAt(self,command,success='OK',error='ERROR',wait=2):
		"""
		Function to send AT commands
		to GSM Module
		"""
		#if not errMain.checkBit('gsmUsb'):
		print '{0:20}'.format(command) ,
		
		try:
			self.obj.write(command+'\r\n')
		except Exception as e:
			self.hotPlug('sendAt(): '+str(e))

		time.sleep(0.25)

		self.status=self.checkStatus(success,error,wait)

		if 'Success' in self.status:
			#errGsm.clearBit(command)
			#errTime.clearBit(command)
			#errUnknown.clearBit(command)
			led.at_status = 1
			return 'Success'
		
		elif 'Timeout' in self.status:
			#errGsm.setBit(command)
			debugLog.error('TIMEOUT=> '+command)
			errTime.setBit(command)
			#errUnknown.clearBit(command)
			led.at_status = 0
			return 'ErrorTimeout'
		
		elif 'Error' in self.status:
			debugLog.error('ERROR=> '+command)
			errGsm.setBit(command)
			#errTime.clearBit(command)
			#errUnknown.clearBit(command)
			led.at_status = 0
			return 'Error'
		
		else:
			#errGsm.clearBit(command)
			#errTime.clearBit(command)
			debugLog.error('OTHER=> '+command)
			errUnknown.setBit(command)
			led.at_status = 0
			return 'Other'

		#else:
		#   print '\n\t\t sendAT: GSM DISCONNECTED'

	def checkStatus(self,success='OK',error='ERROR',wait=3):
		"""
		Function to wait and respond for Replies from modem for each
		AT command sent to it
		"""

		try:
			status = self.obj.read(100).strip()
		except Exception as e:
			status=error
			self.hotPlug('checkStatus: ' + str(e))


		cntr=1                      # Timeout in secs
		while len(status)==0:

			if cntr>wait:
				print '\n\tError, Timeout, cntr = '+str(cntr)+'\n'
				led_q.put((,,,,)) modem_ok("timeout")
				return 'ErrorTimeout'
			else:
				led_q.put((,,,,)) modem_ok("working")
			cntr=cntr+1

			try:
				status = self.obj.read(100).strip()
			except Exception as e:
				status=error
				self.hotPlug('checkStatus(): ' + str(e))

			time.sleep(1)
			if wait>1:         # If waitin for more than 5 sec display count
				print '\n\t'+str(cntr)


		#print '\t((('+status+')))'



		string=status.split('\n')
		string = ''.join(string)
		string = string.replace('\r',' ').replace(',,','; ')


		if success in status:
			#print '\t\t',
			print '{0:20} ==> {1:50}'.format('Success',string)
			return 'Success'  # success => AT Command sent

		elif error in status:
			debugLog.error('\t\t\tReply: '+string)
			print '{0:20} ==> {1:50}'.format('Error',string)
			return 'Error'
		
		else:
			print '{0:20} ==> {1:50}'.format('Other',string)
			return 'Other'

	def gsmInit(self,arg):
		"""
		if errMain.checkBit('gsmUsb'):                  # CHECK IF GSM IS DISCONNECTED FROM RPi
			print "\n\t\tERROR: GSM disconnected !!\n\n"
			time.sleep(1)
			return  'Error'
		else:
		"""

		self.sendAt('at')
		
		if 'CLOSED' not in self.status:
			self.sendAt('at+cipclose=1') # Ref page 27, Fast Closing when cipclose =1
		
		self.sendAt('ate0')

		self.sendAt('at+cpin?')
		
		self.sendAt('at+csq')
		
		self.sendAt('at+creg?')
		
		self.sendAt('at+cgatt?')
		
		self.sendAt('at+cipshut')
		self.sendAt('at+cstt="internet"')

		self.sendAt('at+ciicr','OK','ERROR',20)
		
		self.sendAt('at+cifsr','.','ERROR')

		flagConn = self.sendAt('at+cipstart="TCP","52.74.14.46","5000"','CONNECT OK','FAIL')

		
		if flagConn=='Success':
			return 'Success'
		elif 'Error' in flagConn:
			return 'Error'
		else:
			
			flagCheck = self.checkStatus('CONNECT OK','FAIL',10)
			
			if flagCheck == 'ErrorTimeout':
				errTime.setBit('at+cipstart="TCP","52.74.14.46","5000"')
			elif flagCheck == 'Error':
				errGsm.setBit('at+cipstart="TCP","52.74.14.46","5000"')
			else:
				errGsm.clearBit('at+cipstart="TCP","52.74.14.46","5000"')
				errUnknown.clearBit('at+cipstart="TCP","52.74.14.46","5000"')
			
			return 'Other'




	def sendPacket(self,arg,gsmErr,mainErr,timeoutErr,
		unknownErr,case ='backfill'):
		"""
		if errMain.checkBit('gsmUsb'):

			print '\n\n\tERROR: GSM DISCONNECTED !!'

			return 'Error'
		else:
		""" 
		errMain.clearBit('liveSend')                # IF error this bit 
													 #is set in Live class

		packet = str(arg['dredger_name'])\
				+';'+str(arg['time'])\
				  +';'+str(arg['storage_tank_level'])\
				+';'+str(arg['storage_tank_cap'])\
				+';'+str(arg['service_tank_level'])\
				+';'+str(arg['service_tank_cap'])\
				+';'+str(arg['flowmeter_1_in'])\
				+';'+str(arg['flowmeter_1_out'])\
				+';'+str(arg['engine_1_status'])\
				+';'+str(arg['flowmeter_2_in'])\
				+';'+str(arg['flowmeter_2_out'])\
				+';'+str(arg['engine_2_status'])\
				+';'+str(hex(gsmErr))\
				+';'+str(hex(mainErr))\
				+';'+str(hex(timeoutErr))\
				+';'+str(hex(unknownErr))\


		self.sendAt('at+cipsend','>','ERROR',5)

		try:
			self.obj.write(packet+'\x0A\x0D\x0A\x0D\x1A')
		except Exception as e:
			self.hotPlug('sendPacket(): '+str(e))

		flagStatus = self.checkStatus('SEND OK','FAIL',3)

		if flagStatus == 'ErrorTimeout':
			errTime.setBit('at+cipsend')
		elif flagStatus=='Error':
			errGsm.setBit('at+cipsend')
		else:
			errGsm.clearBit('at+cipsend')

		print "\n\nPacket: \t"+packet+"\n\n"
		
		return flagStatus

class backFill(threading.Thread):

	def __init__(self,event):
		threading.Thread.__init__(self)
		self.db=database_backup()
		self.gsm = Sim900()

	def run(self):
		i=1
		while True:
			event.wait()
			backfillEvent.clear()

			arg = self.db.fetchData()
			if not arg:
				print 'Database is empty'
				led.comm_status = 2
				time.sleep(1)
			else:
				
				self.gsm.sendAt('at+cipclose=1')
				

				flagConn = self.gsm.sendAt('at+cipstart="TCP","52.74.14.46","5000"','CONNECT OK','FAIL')

				if flagConn!='Success':
					self.gsm.checkStatus('CONNECT OK','FAIL',10)
				
				flagSend=self.gsm.sendPacket(arg,arg['errGsm'],
					arg['errMain'],arg['errTimeout'],arg['errUnknown'],'backfill')

				if flagSend == 'Success':
					backLog.info('SUCCESS=> Packet: '+str(arg['time']))
					debugLog.critical('BACKFILL :SUCCESS=> Packet: '+str(arg['time']))
					print '\n\n\tBACKFILL : DATA SENDING SUCCESS . .\n\n'
					led.comm_status = 2
					self.db.deleteDb(arg)

				elif 'Error' in  flagSend:
					backLog.error('FAILED=> Packet: '+str(arg['time']))
					debugLog.critical('BACKFILL :FAILED=> Packet: '+str(arg['time']))
					print '\n\n\tBACKFILL : DATA SENDING FAILED!!\n\n'
					time.sleep(5)       # WhY???

				else:
					backLog.error('OTHER=> Packet: '+str(arg['time']))
					debugLog.critical('BACKFILL :OTHER=> Packet: '+str(arg['time']))
					print '\n\n\tBACKFILL : returned "Other" status!!\n\n'
					
				print '\n\nERROR CODE:',hex(arg['errGsm']),hex(arg['errMain']),hex(arg['errTimeout']),hex(arg['errUnknown']),'\n\n'
				time.sleep(0.5)

			backfillEvent.set()


class live(threading.Thread):

	def __init__(self,event):
		self.delta=plc()
		self.db=database_backup()
		threading.Thread.__init__(self)
		self.gsm = Sim900()
		errMain.setBit('boot')          # Bit 'boot' is set for only the first Live packet

	def run(self):
		while True:

			event.clear()
			backfillEvent.wait()
			errMain.Code    =0  #Resetting All error codes for new data
			errGsm.code     =0
			errTime.code    =0
			errUnknown.code =0

			#debugLog.critical('s-------------Live:')
			print 's-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())

			try:
				arg=self.delta.readData()
				flagInit = self.gsm.gsmInit(arg)

				if flagInit == 'Success' or flagInit == 'Other':          # Else part is in gsmInit()
					
					if flagInit=='Success':
						#liveLog.info("GsmInit SUCCESS")
						errMain.clearBit('gsmInit')
					else:
						#liveLog.info("GsmInit ERROR")
						errMain.setBit('gsmInit')

					flagSend = self.gsm.sendPacket(arg,errGsm.code,errMain.code,
						errTime.code,errUnknown.code,'live')

					if 'Error' in flagSend:
						errMain.setBit('liveSend')
						debugLog.critical('LIVE :FAILED=> Packet: '+str(arg['time']))
						liveLog.error('FAILED=> Packet: '+str(arg['time']))
						print '\n\n\tLIVE : DATA SENDING FAILED!!\n\n'
						self.db.insertDb(arg,errGsm.code,errMain.code,errTime.code,errUnknown.code)

					elif flagSend == 'Success':
						debugLog.critical('LIVE :SUCCESS=> Packet: '+str(arg['time']))
						liveLog.info('SUCCESS=> Packet: '+str(arg['time']))
						print '\n\n\tLIVE : DATA SENDING SUCCESS . .\n\n'
						led.comm_status = 1

					elif flagSend=='ErrorTimeout':
						liveLog.error('CIPSEND Timeout=> Packet: '+str(arg['time']))
						debugLog.critical('LIVE : CIPSEND Timeout=> Packet: '+str(arg['time']))
						errTime.setBit('at+cipsend')
						print '\n\n\tLIVE : DATA SENDING FAILED!! (CIPSEND Timeout)\n\n'
						self.db.insertDb(arg,errGsm.code,errMain.code,errTime.code,errUnknown.code)

					else:
						liveLog.error('Returned "Other" status,packet: '+str(arg['time']))
						debugLog.error('Returned "Other" status')
						errUnknown.setBit('liveSend')
						print '\n\n\tLIVE :returned "Other" status!!\n\n'
						self.db.insertDb(arg,errGsm.code,errMain.code,errTime.code,errUnknown.code)
				else:
					#liveLog.error("GsmInit ERROR")
					liveLog.error('FAILED=> DATA SENDING FAILED,packet: '+str(arg['time']))
					errMain.setBit('gsmInit')
					errMain.setBit('liveSend')

					self.db.insertDb(arg,errGsm.code,errMain.code,errTime.code,errUnknown.code)
					
					debugLog.critical('Error in gsmInit,PACKET PUSHED TO BACKUP db,packet: '+str(arg['time']))
					print "\n\t\tError in gsmInit\
						\n\t\tPACKET PUSHED TO BACKUP db\n\n"


					


			except Exception as e:
				liveLog.error('LIVE : EXCEPTION, '+str(e))
				print 'Error, live_run: '+str(e)

			errMain.clearBit('boot')        #Bit boot is cleared for all packets except the 1st Live

			print '\n\nERROR CODE:',hex(errGsm.code),hex(errMain.code),hex(errTime.code),hex(errUnknown.code),'\n\n'

			#debugLog.critical('e-------------Live:')
			print 'e-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())

			event.set()

			time.sleep(20)                   #backfill runs for 20 sec's

def main():
	t1 = backFill(event)
	t2 = live(event)
	t1.start()
	t2.start()



if __name__ == '__main__':
	
	led_q.put((,,,,)) code_status()

	try:
		os.system("clear")
	except :
		pass
	led_q = Queue.Queue()

	#debugLog    = log.debugLog('./log/dredger2_debug')         # Code for PC
	#liveLog     = log.liveLog('./log/dredger2_live')
	#backLog     = log.backfillLog('./log/dredger2_backfill')

	debugLog    = log.debugLog('/home/pi/Desktop/RPi/log/dredger2_debug')         # Code for Beagle
	liveLog     = log.liveLog('/home/pi/Desktop/RPi/log/dredger2_live')
	backLog     = log.backfillLog('/home/pi/Desktop/RPi/log/dredger2_backfill')

	debugLog.critical("____________BOOT____________")
	liveLog.critical("____________BOOT____________")
	backLog.critical("____________BOOT____________")

	event = threading.Event()
	backfillEvent = threading.Event()
	backfillEvent.set()
	errMain = errorHandlerMain()           # import from file errorFile.py
	errGsm = errorHandlerGsm()           # import from file errorFile.py
	errTime = errorHandlerTimeout()           # import from file errorFile.py
	errUnknown = errorHandlerUnknown()       # import from file errorFile.py


	main()
