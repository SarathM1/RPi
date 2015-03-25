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
	def sendAtCommand(self,code,command):
		self.serialPort.write(bytes(command+'\r\n',encoding='ascii'))
		self.status =  self.readCommandResponse(code,command)
		#return self.status
		print (self.status)

	def readCommandResponse(self,code,command):
		time.sleep(0.25)
		try:
			msg = self.serialPort.read(100).decode('ascii').strip()
			if not msg:
				msg='(('+code+'))'+'gsmError-->'+command
			else:
				msg='(('+code+'))'+'gsmSucce-->'+ msg +'   (' +command+')'
			#print ('In functn,msg =',msg,' type = ',type(msg))
			return msg
		except Exception as e:
			print('Sim900:'+str(e))
			return 'gsmExcep'
		if msg:
			return msg

	def __del__(self):
		self.serialPort.close()





def db_init():
	conn = sqlite3.connect("backup.db")
	c=conn.cursor()
	try:
		c.execute("CREATE TABLE table1(device TEXT,level INT,time TEXT)")
		conn.close()
	except Exception as e:
		print ('db_init ERROR:'+str(e))
		pass

def sendPacket(code,packet):
	modem = Sim900('/dev/ttyS0')
	modem.sendAtCommand(code,'ATE0')
	modem.sendAtCommand(code,'AT')
	if code=='thread':
		modem.sendAtCommand(code,'AT+CIPSTART="UDP","52.74.32.242","50002"')#52.74.32.242
	else:
		modem.sendAtCommand(code,'AT+CIPSTART="UDP","52.74.32.242","50001"')#52.74.32.242
	modem.sendAtCommand(code,'AT+CIPSEND')
	modem.sendAtCommand(code,packet)
	temp = modem.status.split('-')
	temp = temp[0]
	if temp == 'gsmError' :
		flag = 'sendError'
	else:
		flag= 'success'
	modem.sendAtCommand(code,'AT+CIPCLOSE')
	
	return flag	
	
class workerThread(threading.Thread):
	
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		
		print ('In Thread\n\n')
		while True:
			conn = sqlite3.connect("backup.db")
			c=conn.cursor()
			c.execute("SELECT * FROM table1 ORDER BY ROWID")
			data = c.fetchall()
			conn.close()
			for item in data:
				try:
					#packet = str(item[0]) + ';' + str(item[1]) + ';' + str(item[2]) +'\x1A'
					packet = 'backfill' + ';' + str(item[1]) + ';' + str(item[2]) +'\x1A'
					print ('_________In thread________' )
					
					flag=sendPacket('thread',packet)
					if flag ==	'sendError':
						print ('Sending failed')
					else:
						print ('Sending success(thread):'+packet)
						conn1 = sqlite3.connect("backup.db")
						c=conn1.cursor()
						sql = "DELETE FROM table1 WHERE time=? and level=?"
						c.execute(sql,[item[2],item[1]])
						conn1.commit()
						conn1.close()
						
					
				except Exception as e:
					print('Error inThread')
					PrintException()
					continue

def Main():
	conn = sqlite3.connect("backup.db")
	c=conn.cursor()
	level='0'
	device = 'live'
	while True:
		try:
			print('s----------------------------------------------------')
			##################################################################################################
			#making packet
			level = str(int(level)+1)                #<--------- level should be read here
			currentTime = time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())
			packet = device + ';' + str(level) + ';' + str(currentTime)+'\x1A'
			##################################################################################################
			#Packet sending and verification
			flag = sendPacket('main',packet)  				#<----------flag checks whether sending is succesful
			
			if flag ==	'sendError':
				print ('Sending failed')
				c.execute("INSERT INTO table1 values(?,?,?)",( 'backup',str(level),str(currentTime) ))
				conn.commit()
			else:
				print ('Sending success:'+packet)
				
			###################################################################################################

			print('e----------------------------------------------------')
			time.sleep(1)
		except serial.SerialException as e:
			print('\nMain Program aborted:' )
			PrintException()
			continue

if __name__ == '__main__':
	thread = workerThread()
	thread.start()
	db_init()
	Main()


		



