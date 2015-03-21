#!/usr/bin/python

import socket
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 
from datetime import datetime
import logging
import logging.handlers


Base = declarative_base()

#Setting up logging defaults
#LOG_FILENAME = "/tmp/udpserver.log"
#LOG_LEVEL = logging.DEBUG

#logger = logging.getLogger(__name__)

#Giving the logger a unique name
#logger.setLevel(LOG_LEVEL)

#Make a handler that writes to a file at midnight and keeping 3 days backup
#andler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
#Formatting each message
#formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
#Attaching format to handler
#handler.setFormatter(formatter)
#Attach the handler to the logger
#logger.addHandler(handler)

"""
Declaring the tables in the database
DB name : dreadger
Table name : dieselLevel
"""
# Declaring the fields in the database using the ORM(Object relational mapper) library
class DieselLevel(Base):
	__tablename__ = 'dieselLevel'
	id = Column(Integer, primary_key=True)
	device = Column(String(25))
	level = Column(Integer)
	mTime = Column(DateTime)
	ip = Column(String(15))

	def __init__(self, device, level, mTime, ip):
		self.device = device
		self.level = level
		self.mTime = mTime
		self.ip = ip

##Logging in as admin 
##creating a mysql database object object 
engine = create_engine('mysql://root:aaggss@localhost/dreadger')

# packet should be or the format given below
# "ABC123;1000;15/9/2014 13:10"
""" This function splits the string into a tuple containing device, level, datetime 
the function parameter should be a string 
return type is a (devicename,level,datetime)
"""
def parsedata(data):
	data = data.strip()		# It removes all the newline character from the string
	data = data.split(';')	# Splits the string at every ';' character
	device = data[0]	
	level = int(data[1])
	time = datetime.strptime( data[2], "%d/%m/%Y %H:%M:%S") # "21/11/06 16:30:40"
	return (device, level, time)


## Main function 
## Here the code for opening the port is written.
if __name__ == '__main__':	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creating a udp socket object 
	HOST = '127.0.0.1'		# It is not reqiured for udp server. for udp client specify the host address 
	PORT = 50001	# It is port number on which communications occur 
	try :
		sock.bind((HOST,PORT))	# Getting the socket ready for communication at the port 50002
		print 'bind done'
	except socket.error, msg: 	#	failure code. If the socket is not created, it will exit.
		#logger.error( 'Bind failed. Error code: ' + str(msg))
		print msg
		sys.exit()

	#logger.info('Socket binding complete') # Will log if socket is created sucessfully.

	session = sessionmaker() 
	session.configure(bind=engine)
	while 1: #infinite loop running to see if packets are coming to the server.
		data, addr = sock.recvfrom(256) # Recieving 256 bits from the port.
		try:
			device, level, time = parsedata(data)
			ip,port = addr
			s = session()
			s.add(DieselLevel(device, level, time, ip))
			print 'data: '+device,level,time,ip
			"""
			logger.debug ('Data packet recieved')
			logger.debug('From : %s' %str(addr))
			logger.debug('Device : ' + device)
			logger.debug('Level : %d' %level)
			logger.debug('Time : %s' %(str(time)))"""

			s.commit()
		except Exception as e:
			print e
			#logger.error('Unable to parse the packet')

	s.close() 	
		
