
#!/usr/bin/python3
import serial
import time
import threading
from backfill import database_backup
from errorFile import errorHandler      # Import from local file errorFile
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
			self.instrument = minimalmodbus.Instrument('/dev/port1',1)
			self.instrument.serial.baudrate = 9600
			self.instrument.serial.bytesize = 7
			self.instrument.serial.parity = serial.PARITY_EVEN
			self.instrument.serial.stopbits = 1
			self.instrument.serial.timeout = 0.1
			self.instrument.mode = minimalmodbus.MODE_ASCII
			print("\n\t\t\tclearBit('plcUsb')")
			err.clearBit('plcUsb')

		except serial.SerialException:
			print("\n\t\t\tsetBit('plcUsb')")
			err.setBit('plcUsb')
			print ('\n\t\tPLC: CANNOT OPEN PORT!!')

		except Exception as e:
			print('\nplc_init: '+str(e)+'\n')
			print("\n\t\t\tsetBit('plcUsb')")
			err.setBit('plcUsb')                               # Error code for logging

	def readData(self):
		cap=['Close','Open']
		status=['Off','On']
		arg={}

		try:

			if err.checkBit('plcUsb'):       # If PLC is disconnected
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
				print("\n\t\t\tclearBit('plcUsb')")
				err.clearBit('plcComm')


		except Exception as e:
				print('PLC_read_data: ',str(e))
				print("\n\t\t\tsetBit('plcUsb')")
				err.setBit('plcComm')

				arg = dummyPacket()

		return arg

class Sim900():
	def __init__ (self):
		try:
			self.obj = serial.Serial(port='/dev/port2', baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,\
			 stopbits=serial.STOPBITS_ONE, timeout=1.0, xonxoff=False, rtscts=False,\
			  writeTimeout=1.0, dsrdtr=False, interCharTimeout=None)

			print("\n\t\t\tclearBit('gsmUsb')")
			err.clearBit('gsmUsb')
		except serial.SerialException:
			print("\n\t\t\tsetBit('gsmUsb')")
			err.setBit('gsmUsb')
			print ('\n\t\tGSM: CANNOT OPEN PORT!!')
		except Exception as e:
			print("\n\t\t\tsetBit('gsmUsb')")
			err.setBit('gsmUsb')
			print('Sim900, __init__:- '+str(e))
		self.db=database_backup()
	def sendAt(self,command,success='OK',error='ERROR',wait=1):
		"""
		Function to send AT commands
		to GSM Module
		"""
		if not err.checkBit('gsmUsb'):
			print('{0:20}'.format(command), end=' ')
			self.obj.write(bytes(command+'\r\n',encoding='ascii'))
			time.sleep(0.25)

			status=self.checkStatus(success,error,wait)
			#time.sleep(1)
			return status
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
				return 'Error'
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
			return 'other'

	def gsmInit(self,arg):
		if err.checkBit('gsmUsb'):                  # CHECK IF GSM IS DISCONNECTED FROM RPi
			print ("\n\t\tERROR: GSM disconnected !!\n\n")
			time.sleep(1)
			return  'Error'
		else:

			self.sendAt('at')
			self.sendAt('at+cipclose')
			self.sendAt('ate0')

			flagCpin = self.sendAt('at+cpin?')
			if 'Error' in flagCpin:
				print("\n\t\t\tsetBit('gsmCpin')")
				err.setBit('gsmCpin')
			else:
				print("\n\t\t\tclearBit('gsmCpin')")
				err.clearBit('gsmCpin')


			flasgCsq = self.sendAt('at+csq')
			if 'Error' in flasgCsq:
				print("\n\t\t\tsetBit('gsmCsq')")
				err.setBit('gsmCsq')
			else:
				print("\n\t\t\tclearBit('gsmCsq')")
				err.clearBit('gsmCsq')

			flagCreg = self.sendAt('at+creg?')
			if 'Error' in flagCreg:
				print("\n\t\t\tsetBit('gsmCreg')")
				err.setBit('gsmCreg')
			else:
				print("\n\t\t\tclearBit('gsmCreg')")
				err.clearBit('gsmCreg')

			flagCgatt = self.sendAt('at+cgatt?')
			if 'Error' in flagCgatt:
				print("\n\t\t\tsetBit('gsmCgatt')")
				err.setBit('gsmCgatt')
			else:
				print("\n\t\t\tclearBit('gsmCgatt')")
				err.clearBit('gsmCgatt')


			self.sendAt('at+cipshut')
			status=self.sendAt('at+cstt="internet"')

			flagCiicr = self.sendAt('at+ciicr','OK','ERROR',20)
			if 'Error' in flagCiicr:
				print("\n\t\t\tsetBit('gsmCiicr')")
				err.setBit('gsmCiicr')
			else:
				print("\n\t\t\tclearBit('gsmCiicr')")
				err.clearBit('gsmCiicr')

			self.sendAt('at+cifsr','.','ERROR')

			flagConn = self.sendAt('at+cipstart="TCP","52.74.229.218","5000"','CONNECT OK','FAIL')
			self.checkStatus('ACK_FROM_SERVER','ERROR',5)


			if flagConn=='Success':
				print("\n\t\t\tclearBit('gsmConn')")
				err.clearBit('gsmConn')
				return 'Success'
			else:
				print("\n\t\t\tsetBit('gsmConn')")
				err.setBit('gsmConn')
				return 'Error'




	def sendPacket(self,arg,case ='backfill'):
		if err.checkBit('gsmUsb'):

			print ('\n\n\tERROR: GSM DISCONNECTED !!')

			return 'Error'
		else:

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
					+';'+str(err.code)


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
				flagSend=self.gsm.sendPacket(arg,'backfill')

				if flagSend == 'Success':
					
					print('\n\n\tBACKFILL : DATA SENDING SUCCESS . .\n\n')
					self.db.deleteDb(arg)

				elif flagSend == 'Error':
					
					print('\n\n\tBACKFILL : DATA SENDING FAILED!!\n\n')
					time.sleep(5)

				else:
					print('\n\n\tBACKFILL : returned "Other" status!!\n\n')
					

				time.sleep(0.5)

			backfillEvent.set()


class live(threading.Thread):

	def __init__(self,event):
		self.delta=plc()
		self.db=database_backup()
		threading.Thread.__init__(self)
		self.gsm = Sim900()
		print("\n\t\t\tsetBit('boot')")
		err.setBit('boot')          # Bit 'boot' is set for only the first Live packet

	def run(self):
		while True:

			event.clear()
			backfillEvent.wait()

			print('s-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))

			try:
				arg=self.delta.readData()
				flagInit = self.gsm.gsmInit(arg)

				if flagInit == 'Success':          # Else part is in gsmInit()

					flagSend = self.gsm.sendPacket(arg,'live')

					if flagSend == 'Error':

						print('\n\n\tLIVE : DATA SENDING FAILED!!\n\n')
						self.db.insertDb(arg,err.code)

					elif flagSend == 'Success':

						print('\n\n\tLIVE : DATA SENDING SUCCESS . .\n\n')

					else:

						print('\n\n\tLIVE :returned "Other" status!!\n\n')
						self.db.insertDb(arg,err.code)

				else:

					self.db.insertDb(arg,err.code)
					print("\n\t\tError in gsmInit\
						\n\t\tPACKET PUSHED TO BACKUP db\n\n")


			except Exception as e:
				print('Error, live_run: '+str(e))

			print("\n\t\t\tclearBit('boot')")
			err.clearBit('boot')		#Bit boot is cleared for all packets except the 1st Live
			print('e-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))

			event.set()

			time.sleep(10)                   #backfill runs for 10 sec's

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
	err = errorHandler()           # import from file errorFile.py
	main()
