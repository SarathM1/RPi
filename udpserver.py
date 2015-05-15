#!/usr/bin/python

import socket
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base 
from sqlalchemy.orm import sessionmaker 
from datetime import datetime


Base = declarative_base()



"""
Declaring the tables in the database
DB name : dreadger
Table name : db
"""
# Declaring the fields in the database using the ORM(Object relational mapper) library
class dreadger(Base):
    __tablename__ = 'db'
    id                  = Column(Integer, primary_key=True)
    dreadger_name       = Column(String(25))
    time                = Column(DateTime,unique=True)  # If not unique then there will be logical errors
    storage_tank_level  = Column(Integer)
    storage_tank_cap    = Column(String(25))
    service_tank_level  = Column(Integer)
    service_tank_cap    = Column(String(25))
    flowmeter_1_in      = Column(Integer)
    flowmeter_1_out     = Column(Integer)
    engine_1_status     = Column(String(25))
    flowmeter_2_in      = Column(Integer)
    flowmeter_2_out     = Column(Integer)
    engine_2_status     = Column(String(25))

    def __repr__(self):
        return self.dreadger_name+ ',' +str(self.time)+ ',' +str(self.storage_tank_level)+ ',' +\
                self.storage_tank_cap+ ',' +str(self.service_tank_level)+ ',' +self.service_tank_cap+ ',' +\
                str(self.flowmeter_1_in)+ ',' +str(self.flowmeter_1_out)+ ',' +self.engine_1_status+ ',' +str(self.flowmeter_2_in)+ ',' +\
                str(self.flowmeter_2_out)+ ',' +str(self.engine_2_status)+'\n'

    def __init__(self, arg):
        
        self.dreadger_name       = arg['dreadger_name']
        self.time                = arg['time']
        self.storage_tank_level  = arg['storage_tank_level']
        self.storage_tank_cap    = arg['storage_tank_cap']
        self.service_tank_level  = arg['service_tank_level']
        self.service_tank_cap    = arg['service_tank_cap']
        self.flowmeter_1_in      = arg['flowmeter_1_in']
        self.flowmeter_1_out     = arg['flowmeter_1_out']
        self.engine_1_status     = arg['engine_1_status']
        self.flowmeter_2_in      = arg['flowmeter_2_in']
        self.flowmeter_2_out     = arg['flowmeter_2_out']
        self.engine_2_status     = arg['engine_2_status']


##creating a mysql database object object 
engine = create_engine('mysql://root:aaggss@localhost/dreadger')

# packet should be or the format given below
# "ABC123;1000;15/9/2014 13:10"

def parsedata(data):
    """ 
    This function splits the string into a tuple containing device, level, datetime 
    the function parameter should be a string 
    return type is a (devicename,level,datetime)
    """
    data = data.strip()     # It removes all the newline character from the string
    data = data.split(';')  # Splits the string at every ';' character
    dictRow={}
    dictRow['dreadger_name']       = data[0]
    dictRow['time']                = datetime.strptime( data[2], "%d/%m/%Y %H:%M:%S")
    dictRow['storage_tank_level']  = int(data[2])
    dictRow['storage_tank_cap']    = data[3]
    dictRow['service_tank_level']  = int(data[4])
    dictRow['service_tank_cap']    = data[5]
    dictRow['flowmeter_1_in']      = int(data[6])
    dictRow['flowmeter_1_out']     = int(data[7])
    dictRow['engine_1_status']     = data[8]
    dictRow['flowmeter_2_in']      = int(data[9])
    dictRow['flowmeter_2_out']     = int(data[10])
    dictRow['engine_2_status']     = data[11]

    return (dictRow)


## Main function 
## Here the code for opening the port is written.
if __name__ == '__main__':  
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creating a udp socket object 
    HOST = '127.0.0.1'      # It is not reqiured for udp server. for udp client specify the host address 
    PORT = 50001    # It is port number on which communications occur 
    try :
        sock.bind((HOST,PORT))  # Getting the socket ready for communication at the port 50002
        print 'bind done'
    except socket.error, msg:   #   failure code. If the socket is not created, it will exit.
        print msg
        sys.exit()

    

    session = sessionmaker() 
    session.configure(bind=engine)
    while 1: #infinite loop running to see if packets are coming to the server.
        data, addr = sock.recvfrom(256) # Recieving 256 bits from the port.
        try:
            #device, level, time = parsedata(data)
            #ip,port = addr
            #s = session()
            #s.add(dreadger(device, level, time, ip))
            print 'data: '+ data.strip.split(';')
            

            s.commit()
        except Exception as e:
            print e
            

    s.close()   
        
