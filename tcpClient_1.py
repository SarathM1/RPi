
#!/usr/bin/python3
import serial
import time
import threading
from backfill import database_backup
from errorFile1 import errorHandlerMain      # Import from local file errorFile1
from errorFile1 import errorHandlerGsm      # Import from local file errorFile1
from errorFile1 import errorHandlerTimeout      # Import from local file errorFile1
from errorFile1 import errorHandlerUnknown      # Import from local file errorFile1

import minimalmodbus
import os
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

	arg['dredger_name']         = 'dredger1'
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
			self.instrument = minimalmodbus.Instrument('/dev/port1',2)
			self.instrument.serial.baudrate = 9600
			self.instrument.serial.bytesize = 7
			self.instrument.serial.parity = serial.PARITY_EVEN
			self.instrument.serial.stopbits = 1
			self.instrument.serial.timeout = 0.1
			self.instrument.mode = minimalmodbus.MODE_ASCII
			errMain.clearBit('plcUsb')

		except serial.SerialException:
			errMain.setBit('plcUsb')
			print ('\n\t\tPLC: CANNOT OPEN PORT!!')

		except Exception as e:
			print('\nplc_init: '+str(e)+'\n')
			errMain.setBit('plcUsb')                               # Error code for logging

	def readData(self):
		cap=['Close','Open']
		status=['Off','On']
		arg={}

		try:

			if errMain.checkBit('plcUsb'):       # If PLC is disconnected
				print ('\n\t\tERROR: PLC DISCONNECTED !!\
					\n\r\t\tRETURNING DUMMY PACKET\n\n')
				arg = dummyPacket()

			else:

				arg['dredger_name']         = 'dredger1'
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
				print("\n\t\tDATA READ FROM PLC!!\n\n")
				errMain.clearBit('plcComm')


		except Exception as e:
				print('PLC_read_data: ',str(e))
				errMain.setBit('plcComm')

				arg = dummyPacket()

		return arg

class Sim900():
	def __init__ (self):
		try:
			self.obj = serial.Serial(port='/dev/ttyS0', baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,\
			 stopbits=serial.STOPBITS_ONE, timeout=1.0, xonxoff=False, rtscts=False,\
			  writeTimeout=1.0, dsrdtr=False, interCharTimeout=None)

			errMain.clearBit('gsmUsb')
		except serial.SerialException:
			errMain.setBit('gsmUsb')
			print ('\n\t\tGSM: CANNOT OPEN PORT!!')
		except Exception as e:
			errMain.setBit('gsmUsb')
			print('Sim900, __init__:- '+str(e))
		self.db=database_backup()
	def sendAt(self,command,success='OK',error='ERROR',wait=2):
		"""
		Function to send AT commands
		to GSM Module
		"""
		if not errMain.checkBit('gsmUsb'):
			print('{0:20}'.format(command), end=' ')
			self.obj.write(bytes(command+'\r\n',encoding='ascii'))
			time.sleep(0.25)

			status=self.checkStatus(success,error,wait)

			if 'Success' in status:
				#errGsm.clearBit(command)
				#errTime.clearBit(command)
				#errUnknown.clearBit(command)
				return 'Success'
			
			elif 'Timeout' in status:
				#errGsm.setBit(command)
				errTime.setBit(command)
				#errUnknown.clearBit(command)
				return 'ErrorTimeout'
			
			elif 'Error' in status:
				errGsm.setBit(command)
				#errTime.clearBit(command)
				#errUnknown.clearBit(command)
				return 'Error'
			else:
				#errGsm.clearBit(command)
				#errTime.clearBit(command)
				errUnknown.setBit(command)
				return 'Other'
				
			
			#time.sleep(1)
			#return status
		else:
			print('\n\t\t sendAT: GSM DISCONNECTED')

	def checkStatus(self,success='OK',error='ERROR',wait=3):
		"""
		Function to wait and respond for Replies from modem for each
		AT command sent to it
		"""

		try:

			status = self.obj.read(100).decode('ascii').strip()
		except Exception as e:
			status=error
			print('checkStatus: ' + str(e))


		cntr=1                      # Timeout in secs
		while len(status)==0:

			if cntr>wait:
				print('\n\tError, Time out, cntr = '+str(cntr)+'\n')
				return 'ErrorTimeout'
			cntr=cntr+1

			try:
				status = self.obj.read(100).decode('ascii').strip()
			except Exception as e:
				status=error
				print(e)

			time.sleep(1)
			if wait>1:         # If waitin for more than 5 sec display count
				print('\n\t'+str(cntr))


		#print '\t((('+status+')))'



		string=status.split('\n')
		string = ''.join(string)
		string = string.replace('\r',' ').replace(',,','; ')


		if success in status:
			#print '\t\t',
			print('{0:20} ==> {1:50}'.format('Success',string))
			return 'Success'  # success => AT Command sent

		elif error in status:
			print('{0:20} ==> {1:50}'.format('Error',string))
			return 'Error'
		
		else:
			print('{0:20} ==> {1:50}'.format('Other',string))
			return 'Other'

	def gsmInit(self,arg):
		if errMain.checkBit('gsmUsb'):                  # CHECK IF GSM IS DISCONNECTED FROM RPi
			print ("\n\t\tERROR: GSM disconnected !!\n\n")
			time.sleep(1)
			return  'Error'
		else:

			self.sendAt('at')
			
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

			flagConn = self.sendAt('at+cipstart="TCP","52.74.229.218","5000"','OK','FAIL')
			self.checkStatus('CONNECT OK','FAIL',10)
			#self.checkStatus('ACK_FROM_SERVER','ERROR',3)

			


			if flagConn=='Success':
				return 'Success'
			elif 'Error' in flagConn:
				return 'Error'
			else:
				return 'Other'




	def sendPacket(self,arg,gsmErr,mainErr,timeoutErr,
		unknownErr,case ='backfill'):
		if errMain.checkBit('gsmUsb'):

			print ('\n\n\tERROR: GSM DISCONNECTED !!')

			return 'Error'
		else:
			
			errMain.clearBit('liveSend')				# IF error this bit 
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
			self.obj.write(bytes(packet+'\x0A\x0D\x0A\x0D\x1A',encoding='ascii'))
			flagStatus = self.checkStatus('SEND OK','ERROR',3)


			print("\n\nPacket: \t"+packet+"\n\n")

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
				print ('Database is empty')
				time.sleep(1)
			else:
				
				self.gsm.sendAt('at+cipclose=1')
				

				flagConn = self.gsm.sendAt('at+cipstart="TCP","52.74.229.218","5000"','OK','FAIL')
				self.gsm.checkStatus('CONNECT OK','FAIL',10)
				
				flagSend=self.gsm.sendPacket(arg,arg['errGsm'],
					arg['errMain'],arg['errTimeout'],arg['errUnknown'],'backfill')

				if flagSend == 'Success':
					print('\n\n\tBACKFILL : DATA SENDING SUCCESS . .\n\n')
					self.db.deleteDb(arg)

				elif 'Error' in  flagSend:
					print('\n\n\tBACKFILL : DATA SENDING FAILED!!\n\n')
					time.sleep(5)		# WhY???

				else:
					print('\n\n\tBACKFILL : returned "Other" status!!\n\n')
					
				print ('\n\nERROR CODE:',hex(arg['errGsm']),hex(arg['errMain']),hex(arg['errTimeout']),hex(arg['errUnknown']),'\n\n')
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
			errMain.Code 	=0  #Resetting All error codes for new data
			errGsm.code 	=0
			errTime.code 	=0
			errUnknown.code =0

			print('s-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))

			try:
				arg=self.delta.readData()
				flagInit = self.gsm.gsmInit(arg)

				if flagInit == 'Success' or flagInit == 'Other':          # Else part is in gsmInit()
					
					if flagInit=='Success':
						errMain.clearBit('gsmInit')
					else:
						errMain.setBit('gsmInit')

					flagSend = self.gsm.sendPacket(arg,errGsm.code,errMain.code,
						errTime.code,errUnknown.code,'live')

					if 'Error' in flagSend:
						errMain.setBit('liveSend')
						print('\n\n\tLIVE : DATA SENDING FAILED!!\n\n')
						self.db.insertDb(arg,errGsm.code,errMain.code,errTime.code,errUnknown.code)

					elif flagSend == 'Success':
						print('\n\n\tLIVE : DATA SENDING SUCCESS . .\n\n')

					elif flagSend=='ErrorTimeout':
						errTime.setBit('at+cipsend')
						print('\n\n\tLIVE : DATA SENDING FAILED!! (CIPSEND Timeout)\n\n')
						self.db.insertDb(arg,errGsm.code,errMain.code,errTime.code,errUnknown.code)

					else:
						errUnknown.setBit('liveSend')
						print('\n\n\tLIVE :returned "Other" status!!\n\n')
						self.db.insertDb(arg,errGsm.code,errMain.code,errTime.code,errUnknown.code)
				else:
					errMain.setBit('gsmInit')
					errMain.setBit('liveSend')
					self.db.insertDb(arg,errGsm.code,errMain.code,errTime.code,errUnknown.code)
					print("\n\t\tError in gsmInit\
						\n\t\tPACKET PUSHED TO BACKUP db\n\n")


					


			except Exception as e:
				print('Error, live_run: '+str(e))

			errMain.clearBit('boot')		#Bit boot is cleared for all packets except the 1st Live

			print ('\n\nERROR CODE:',hex(errGsm.code),hex(errMain.code),hex(errTime.code),hex(errUnknown.code),'\n\n')
			print('e-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))

			event.set()

			time.sleep(20)                   #backfill runs for 20 sec's

def main():
	t1 = backFill(event)
	t2 = live(event)
	t1.start()
	t2.start()



if __name__ == '__main__':
	try:
		os.system("clear")
	except :
		pass
	event = threading.Event()
	backfillEvent = threading.Event()
	backfillEvent.set()
	errMain = errorHandlerMain()           # import from file errorFile1.py
	errGsm = errorHandlerGsm()           # import from file errorFile1.py
	errTime = errorHandlerTimeout()           # import from file errorFile1.py
	errUnknown = errorHandlerUnknown()		 # import from file errorFile1.py
	main()
