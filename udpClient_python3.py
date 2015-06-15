
#!/usr/bin/python3
import serial
import time
import threading
import minimalmodbus
import sqlite3
import random
import os

from flask import Flask, flash, request, jsonify, url_for, render_template, redirect
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask (__name__)                  
db = SQLAlchemy(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'backfill.db')

class dredger(db.Model):
    __tablename__ = 'backfill'
    id                  = db.Column(db.Integer, primary_key=True)
    dredger_name       = db.Column(db.String(25))
    #time                = db.Column(db.DateTime,unique=True)  # If not unique then there will be logical errors
    time                = db.Column(db.String(20),unique=True) #Sqlite supports only string as date
    storage_tank_level  = db.Column(db.Integer)
    storage_tank_cap    = db.Column(db.String(25))
    service_tank_level  = db.Column(db.Integer)
    service_tank_cap    = db.Column(db.String(25))
    flowmeter_1_in      = db.Column(db.Integer)
    flowmeter_1_out     = db.Column(db.Integer)
    engine_1_status     = db.Column(db.String(25))
    flowmeter_2_in      = db.Column(db.Integer)
    flowmeter_2_out     = db.Column(db.Integer)
    engine_2_status     = db.Column(db.String(25))

    def __repr__(self):
        return self.dredger_name+ ',' +str(self.time)+ ',' +str(self.storage_tank_level)+ ',' +\
                self.storage_tank_cap+ ',' +str(self.service_tank_level)+ ',' +self.service_tank_cap+ ',' +\
                str(self.flowmeter_1_in)+ ',' +str(self.flowmeter_1_out)+ ',' +self.engine_1_status+ ',' +str(self.flowmeter_2_in)+ ',' +\
                str(self.flowmeter_2_out)+ ',' +str(self.engine_2_status)+'\n'

    def __init__(self, arg):
        
        self.dredger_name       = arg['dredger_name']
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
    

class database_backup():
    def db_init(self):
        try:
            db.create_all()
        except Exception as e:
            print(('db_init ERROR:'+str(e)))
            pass
        
    def drop_all(self):
        db.drop_all()

    def insertDb(self,arg):
        try:
            data=dredger(arg)
            db.session.add(data)
            db.session.commit()
        except Exception as e:
            #flash('insertDb: '+str(e))
            print ('insertDb: '+str(e))

    def deleteDb(self,arg):
        try:
            dredger.query.filter(dredger.time == arg['time']).delete()
            db.session.commit()
        except Exception as e:
            #flash('insertDb: '+str(e))
            print ('deleteDb: '+str(e))
    def fetchData(self):
        try:
            results = dredger.query.order_by(dredger.time.desc()).first()
            if not results:
                return None  # If database is empty
            else:
                dictRow={}
                dictRow['dredger_name']        = results.dredger_name
                dictRow['time']                 = results.time
                dictRow['storage_tank_level']   = results.storage_tank_level
                dictRow['storage_tank_cap']     = results.storage_tank_cap
                dictRow['service_tank_level']   = results.service_tank_level
                dictRow['service_tank_cap']     = results.service_tank_cap
                dictRow['flowmeter_1_in']       = results.flowmeter_1_in
                dictRow['flowmeter_1_out']      = results.flowmeter_1_out
                dictRow['engine_1_status']      = results.engine_1_status
                dictRow['flowmeter_2_in']       = results.flowmeter_2_in
                dictRow['flowmeter_2_out']      = results.flowmeter_2_out
                dictRow['engine_2_status']      = results.engine_2_status
                return dictRow
        except Exception as e:
            #flash('insertDb: '+str(e))
            print ('fetchData: '+str(e))


class plc():
    def __init__(self):
        try:
            self.instrument = minimalmodbus.Instrument('/dev/ttyUSB2',1)
            self.instrument.serial.baudrate = 9600
            self.instrument.serial.bytesize = 7
            self.instrument.serial.parity = serial.PARITY_EVEN
            self.instrument.serial.stopbits = 1
            self.instrument.serial.timeout = 0.1
            self.instrument.mode = minimalmodbus.MODE_ASCII
        except Exception as e:
            print('plc_init: '+str(e))
    def readData(self):
        cap=['Close','Open']
        status=['Off','On']
        arg={}
        arg['dredger_name']         = 'dredger1'
        arg['time']                 = time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())
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

        return arg

class Sim900():
    def __init__ (self):
        try:
            self.obj = serial.Serial('/dev/hackaday2',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,1)
            
        except Exception as e:

            print('Sim900, __init__:- '+str(e))
        self.db=database_backup()
    def sendAt(self,command,success='OK',error='ERROR',wait=1):
        """
        Function to send AT commands
        to GSM Module
        """
        print('{0:20}'.format(command), end=' ')
        self.obj.write(bytes(command+'\r\n',encoding='ascii'))
        time.sleep(0.25)
        
        status=self.checkStatus(success,error,wait)
        return status

    def checkStatus(self,success='OK',error='ERROR',wait=1):
        """
        Function to wait and respond for Replies from modem for each
        AT command sent to it 
        """
        try:
            status = self.obj.read(100).decode('ascii').strip()
        except Exception as e:
            status=error
            print(e)
        
        
        cntr=1                      # Timeout in secs
        while len(status)==0:           
            
            if cntr>wait:
                print('\n\tError, Time out, cntr = '+str(cntr)+'\n')
                return 'connError'
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
            print('{0:20} ==> {1:50}'.format('success',string))
            return 'success'  # success => AT Command sent
        elif error in status:
            print('{0:20} ==> {1:50}'.format('Error',string))
            return 'sendError'
        else:
            print('{0:20} ==> {1:50}'.format('Other',string))
            return 'other'

    def gsmInit(self,arg,case='backfill'):
        #while True:
        self.sendAt('at')
        self.sendAt('at+cipclose')
        self.sendAt('ate0')
        self.sendAt('at+cpin?')
        self.sendAt('at+csq')
        self.sendAt('at+creg?')
        self.sendAt('at+cgatt?')
        self.sendAt('at+cipshut')
        status=self.sendAt('at+cstt="airtelgprs.com"')

        flag = self.sendAt('at+ciicr','OK','ERROR',20)
        self.sendAt('at+cifsr','.','ERROR')

        flag = self.sendAt('at+cipstart="UDP","52.74.236.155","50001"')

        if 'Error' in flag:
            self.db.insertDb(arg)
            print('Error in gsmInit')
            pass
        else:
            self.sendAt('at+cipqsend=1')
            self.sendPacket(arg,case)
            #break
        """if case != 'backfill':
            break"""

    def sendPacket(self,arg,case ='backfill'):
        #flag='dummy value'              # Just to avoid error

        #while 'Error' not in flag:
        #packet=device+';'+str(level)+';'+str(time)
        
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

        self.sendAt('at+cipsend','>','ERROR')
        self.obj.write(bytes(packet+'\x1A',encoding='ascii'))           # bytes(command+'\r\n',encoding='ascii')
        flag = self.checkStatus('DATA ACCEPT',';')

        print("\n\nPacket: \t"+packet+"\n\n")
        
        if case != 'backfill':              # case!='backfill' => live
            if 'Error' in flag:             # Backup data if live sending fails
                print('\n\n\tLIVE : DATA SENDING FAILED!!\n\n')
                self.db.insertDb(arg)
            else:
                print('\n\n\tLIVE : DATA SENDING SUCCESS . .\n\n')
            #break
        elif case=='backfill':
            if flag=='success':    #Delete packet from database once backfill has send it to server succesfully
                print('\n\n\tBACKFILL : DATA SENDING SUCCESS . .\n\n')
                self.db.deleteDb(arg)
            else:
                #print('device = ',case)
                print('\n\n\tBACKFILL : DATA SENDING FAILED!!\n\n')

        



class backFill(threading.Thread):
    
    def __init__(self,event):
        threading.Thread.__init__(self)
        self.event = event
        self.db=database_backup()
        self.gsm = Sim900()

    def run(self):
        i=1
        while True:
            self.event.wait()
            arg = self.db.fetchData()
            if not arg:
                print ('Database is empty')
                time.sleep(1)
            else:
                self.gsm.sendPacket(arg,'backfill')
                time.sleep(1)

class live(threading.Thread):
    def __init__(self,event):
        self.delta=plc()
        threading.Thread.__init__(self)
        self.event = event
        self.gsm = Sim900()
    
    def run(self):
        
        while True:
            
            self.event.clear()             #One event occurs in live thread btw event.clear() and event.wait
            
            print('s-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))
            
            try:
                arg=self.delta.readData()
                print("\n\n\tDATA READ FROM PLC!!\n\n")
                self.gsm.gsmInit(arg,'live')
            except Exception as e:
                print('Error, live_run: '+str(e))
            

            
            print('e-------------Live: ',time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))
            
            self.event.set()  
            
            time.sleep(10)                   #backfill runs for 10 sec's
            
def main():
    db=database_backup()
    db.db_init()
    event = threading.Event()

    t1 = backFill(event)
    t2 = live(event)
    t1.start()
    t2.start()

    

if __name__ == '__main__':
    main()
            

