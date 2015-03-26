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
	def sendAtCommand(self,code,command,event=0):
		if event!=0:								# To avoid at commands being send from thread when live() is active
			while(event.is_set()==False):
				pass
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



class database():

	def db_init(self):
		conn = sqlite3.connect("backup.db")
		c=conn.cursor()
		try:
			c.execute("CREATE TABLE table1(device TEXT,level INT,time TEXT)")
			conn.close()
		except Exception as e:
			print ('db_init ERROR:'+str(e))
			pass
		finally:
			conn.close()
	def fetchData(self):
		conn=sqlite3.connect("backup.db")
		c=conn.cursor()
		c.execute("SELECT * FROM table1 ORDER BY ROWID")
		data=c.fetchall()
		conn.close()
		return data
	def insertDb(self,device,level,currentTime):
		conn=sqlite3.connect("backup.db")
		c=conn.cursor()
		c.execute("INSERT INTO table1 values(?,?,?)",( device,str(level),str(currentTime) ))
		conn.commit()
		conn.close()
	def deleteDb(self,time,level):
		conn=sqlite3.connect("backup.db")
		c=conn.cursor()
		sql = "DELETE FROM table1 WHERE time=? and level=?"
		c.execute(sql,[time,level])
		conn.commit()
		conn.close()


def sendPacket(code,packet,event=0):
	modem = Sim900('/dev/ttyS0')
	modem.sendAtCommand(code,'ATE0',event)
	modem.sendAtCommand(code,'AT',event)
	modem.sendAtCommand(code,'AT+CIPSTART="UDP","52.74.32.242","50001"',event)#52.74.32.242
	modem.sendAtCommand(code,'AT+CIPSEND',event)
	modem.sendAtCommand(code,packet,event)
	temp = modem.status.split('-')
	temp = temp[0]
	if  'gsmError' in temp:
		flag = 'sendError'
	else:
		flag = 'success'
	modem.sendAtCommand(code,'AT+CIPCLOSE',event)
	
	return flag	
	
class backFill(threading.Thread):
	
	def __init__(self,event):
		threading.Thread.__init__(self)
		self.event = event
		self.db=database()
		

	def run(self):
		while True:
			self.event.wait()
			
			data = self.db.fetchData()
			if not data:
				print ('Database is empty')
				time.sleep(1)
			for item in data:
				try:
					#packet = str(item[0]) + ';' + str(item[1]) + ';' + str(item[2]) +'\x1A'
					packet = 'backfill' + ';' + str(item[1]) + ';' + str(item[2]) +'\x1A'
					print ('_________In thread________' )
					
					flag=sendPacket('thread',packet,self.event)
					if flag ==	'sendError':
						print ('Sending failed')
						break
					else:
						print ('Sending success(thread):'+packet)
						self.db.deleteDb(item[2],item[1])
					
					
				except Exception as e:
					print('Error inThread')
					PrintException()
					#continue
				time.sleep(1)

class live(threading.Thread):
	def __init__(self,event):
		
		
		threading.Thread.__init__(self)
		self.db=database()
		self.event = event
		self.level='0'
		self.device = 'live'
		self.currentTime = time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())
	
	def run(self):
		
		while True:
			try:
				self.event.clear()

				#-------------------------------------------------------------------------------------------------# 
				print('s----------------------------------------------------')
				
				#making packet
				self.level = str(int(self.level)+1)                #<--------- level should be read here
				
				packet = self.device + ';' + str(self.level) + ';' + str(self.currentTime)+'\x1A'
				#-------------------------------------------------------------------------------------------------#
				
				#Packet sending and verification
				flag = sendPacket('main',packet)  				#<----------flag checks whether sending is succesful
				print ('flag=',flag)
				if flag ==	'sendError':
					print ('Sending failed')
					self.db.insertDb(self.device,self.level,self.currentTime)
					
				else:
					print ('Sending success:'+packet)
					
				

				print('e----------------------------------------------------')
				#-------------------------------------------------------------------------------------------------#

				self.event.set()
				time.sleep(10)
			except serial.SerialException as e:
				print('\nMain Program aborted:' )
				PrintException()
				#continue

"""
def liveData(event):
	conn = sqlite3.connect("backup.db")
	c=conn.cursor()
	level='0'
	device = 'live'
	while True:
		try:
			self.event.wait()
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
"""
def main():
	db=database()
	db.db_init()
	event = threading.Event()
	t1 = backFill(event)
	t2 = live(event)
	t1.start()
	t2.start()
	t1.join()
	t2.join()

if __name__ == '__main__':
	main()


		



