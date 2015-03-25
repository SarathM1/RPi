#!/usr/bin/python3

import minimalmodbus
import serial
import time
import logging
import sqlite3
import threading
import sys
import linecache


def PrintException():                                         # For printing lineno, filename etc in try, except
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN , LINE {'+str(lineno)+'} "{'+str(line.strip())+'}"): {'+str(exc_obj)+'}')

class Sim900(object):
	
	def __init__ (self,port,baud=9600,bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stop=serial.STOPBITS_ONE, timeout=1):
		self.serialPort = serial.Serial(port,baud,bytesize,parity,stop,timeout)
		#self.check = 'AT+CIPSTART="UDP","52.74.91.12","50001"'
	def sendAtCommand(self,command):
		self.serialPort.write(bytes(command+'\r\n',encoding='ascii'))
		#if self.check in str(bytes(str(command),'UTF-8')):
		self.status =  self.readCommandResponse()
		#else:
		#self.status = 'dummy Ok'
		#time.sleep(2)
		
		return self.status

	def readCommandResponse(self):
		time.sleep(0.25)

		#while True:
		try:

			msg = self.serialPort.read(100).decode('ascii').strip()
			print ('In functn,msg =',msg,' type = ',type(msg))
			return msg
		except Exception as e:
			msg ='ERROR'
			print('msg:'+str(e))
			return msg
			#print (type(self.serialPort.read(100)))
			#print('msg:'+str(e))
			#break
		if msg:
			return msg

	def __del__(self):
		self.serialPort.close()

class workerThread(threading.Thread):

	
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		lock.wait()
		print ('In Thread\n\n')
		while True:
			conn1 = sqlite3.connect("backup.db")
			c=conn1.cursor()
			c.execute("SELECT * FROM table1 ORDER BY ROWID")
			data = c.fetchall()
			conn1.close()
			for item in data:
				try:
					modem = Sim900('/dev/ttyS0')
					modem.sendAtCommand('AT+CIPSTART="UDP","52.74.32.242","50002"')
					#52.74.32.242
					print ('Thread CIPStatus:'+modem.status)
					if   '' in str(bytes(str(modem.status),'UTF-8')) :
						#print ('Error here')
						raise serial.SerialException
					packet = str(item[0]) + ';' + str(item[1]) + ';' + str(item[2]) +'\x1A'
					print ('Thread: '+packet )
					modem.sendAtCommand('AT+CIPSEND')
					modem.sendAtCommand(packet)
					print ('Thread: '+modem.status)
					modem.sendAtCommand('AT+CIPCLOSE')
					conn1 = sqlite3.connect("backup.db")
					c=conn1.cursor()
					sql = "DELETE FROM table1 WHERE time=? and level=?"
					c.execute(sql,[item[2],item[1]])
					conn1.commit()
					conn1.close()
				except Exception as e:
					print('Error inThread')
					PrintException()
					break
			



def db_init():
	#conn = sqlite3.connect("backup.db")
	
	conn2 = sqlite3.connect("backup.db")

	c=conn2.cursor()
	try:
		c.execute("CREATE TABLE table1(device TEXT,level INT,time TEXT)")
		conn2.close
	except:
		pass


if __name__ == '__main__':
	lock = threading.Event()
	db_init()
	#conn = sqlite3.connect("backup.db")
	conn2 = sqlite3.connect("backup.db")

	c=conn2.cursor()
	lock.clear()
	thread = workerThread()
	thread.start()
	while True:
		

		"""try:
			instrument = minimalmodbus.Instrument('/dev/ttyUSB0',1,mode='ASCII')
			instrument.serial.baudrate = 9600
			instrument.serial.bytesize = 7
			instrument.serial.parity = serial.PARITY_EVEN
			instrument.serial.stopbits = 1
			instrument.serial.timeout = 0.1
			instrument.mode = minimalmodbus.MODE_ASCII
		except Exception as e:
			print (e)"""
		
		modem = Sim900('/dev/ttyS0')
	
			
		
		level='0'

		
		device = 'live'
		while True:
			try:
				e = 'ERROR'
				lock.clear()
				#currentTime = time.strftime('%d/%m/%Y %H:%M:%S',time.gmtime())
				#level=30
				level = str(int(level)+1)                                           # level should be read here
				currentTime = time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())
				packet = device + ';' + str(level) + ';' + str(currentTime)+'\x1A'
				#print ('localtime: ' + currentTime)
				

				
				modem.sendAtCommand('AT+CIPSTART="UDP","52.74.32.242","50001"')
				#52.74.32.242
				print (modem.status)

				if 'ERROR' in str(bytes(str(modem.status),'UTF-8'))  or str(bytes(str(modem.status),'UTF-8')) =='':
					#print ('Error here')
					raise serial.SerialException

				modem.sendAtCommand('AT+CIPSEND')
				
				"""try:
					#level = instrument.read_register(4105)
					
				except Exception as e:
					print (e)"""
				#level='2'
				
				#currentTime = time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())
				#packet = device + ';' + str(level) + ';' + str(currentTime)+'\x1A'
				#print ('localtime: ' + currentTime)
				modem.sendAtCommand(packet)
				print (modem.status)
				modem.sendAtCommand('AT+CIPCLOSE')
				#time.sleep(1)
				print('in main,packet: '+packet)
				print('----------------------------------------------------')
				lock.set()
				time.sleep(5)
			except serial.SerialException as e:
				#print (e)
				print (device,str(level),str(currentTime))
				c.execute("INSERT INTO table1 values(?,?,?)",( 'backup',str(level),str(currentTime) ))
				conn2.commit()
				print('\nMain Program aborted:' )
				PrintException()
				continue


		



