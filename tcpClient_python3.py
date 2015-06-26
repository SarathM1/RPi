
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
    arg['error_code']           = err.code

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
        except Exception as e:
            print('\nplc_init: '+str(e)+'\n')
            err.setBit('plc')                               # Error code for logging
            
    def readData(self):
        cap=['Close','Open']
        status=['Off','On']
        arg={}

        try:
            
            if err.checkBit('plc'):       # If PLC is disconnected

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
                arg['error_code']           = err.code


        except Exception as e:
                print('PLC_read_data: ',str(e))

        return arg

class Sim900():
    def __init__ (self):
        try:
            self.obj = serial.Serial('/dev/port2',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,1)
            
        except Exception as e:
            err.setBit('gsmUsb')
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
        #time.sleep(1)
        return status

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
        
        self.sendAt('at')
        self.sendAt('at+cipclose')
        self.sendAt('ate0')
        
        flagCpin = self.sendAt('at+cpin?')
        if 'Error' in flagCpin:
            err.setBit('gsmCpin')
        
        flasgCsq = self.sendAt('at+csq')
        if 'Error' in flasgCsq:
            err.setBit('gsmCsq')

        flagCreg = self.sendAt('at+creg?')
        if 'Error' in flagCreg:
            err.setBit('gsmCreg')
        
        flagCgatt = self.sendAt('at+cgatt?')
        if 'Error' in flagCgatt:
            err.setBit('gsmCgatt')

        
        self.sendAt('at+cipshut')
        status=self.sendAt('at+cstt="internet"')

        flagCiicr = self.sendAt('at+ciicr','OK','ERROR',20)
        if 'Error' in flagCiicr:
            err.setBit('gsmCiicr')

        self.sendAt('at+cifsr','.','ERROR')

        flagConn = self.sendAt('at+cipstart="TCP","54.169.81.50","5000"','CONNECT OK','FAIL')
        self.checkStatus('ACK_FROM_SERVER','ERROR',3)
        
        if 'Error' in flagConn:
            self.setBit('gsmConn')
            self.db.insertDb(arg)
            print('Error in gsmInit')
            pass
        else:
            self.sendPacket(arg,case)

            
    def sendPacket(self,arg,case ='backfill'):
        
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
                +';'+str(arg['error_code'])

        
        self.sendAt('at+cipsend','>','ERROR',5)
        self.obj.write(bytes(packet+'\x0A\x0D\x0A\x0D\x1A',encoding='ascii'))
        flag = self.checkStatus('SEND OK','ERROR',3)

        print("\n\nPacket: \t"+packet+"\n\n")
        
        if case != 'backfill':              # case!='backfill' => live
            if 'Error' in flag:             # Backup data if live sending fails
                print('\n\n\tLIVE : DATA SENDING FAILED!!\n\n')
                self.db.insertDb(arg)
            else:
                print('\n\n\tLIVE : DATA SENDING SUCCESS . .\n\n')
            
        elif case=='backfill':
            if flag=='success':    #Delete packet from database once backfill has send it to server succesfully
                print('\n\n\tBACKFILL : DATA SENDING SUCCESS . .\n\n')
                self.db.deleteDb(arg)
            else:
                print('\n\n\tBACKFILL : DATA SENDING FAILED!!\n\n')

        



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
            if err.checkBit('gsmUsb'):
                if err.checkBit('plc'):                  # CHECK IF GSM IS DISCONNECTED FROM RPi
                        print ("\n\t\tERROR: PLC & GSM disconnected !!\n\n")
                else:
                    print ('\n\n\tERROR: GSM DISCONNECTED !!\
                    PLEASE REBOOT\n\n')

                time.sleep(5)
            else:
                arg = self.db.fetchData()
                if not arg:
                    print ('Database is empty')
                    time.sleep(1)
                else:
                    self.gsm.sendPacket(arg,'backfill')
                    time.sleep(0.5)
            backfillEvent.set()


class live(threading.Thread):
    def __init__(self,event):
        self.delta=plc()
        self.db=database_backup()
        threading.Thread.__init__(self)
        self.gsm = Sim900()
        err.setBit('boot')          # Bit 'boot' is set for only the first Live packet
    def run(self):
        
        while True:
            
            event.clear()
            backfillEvent.wait()
            
            
            if err.checkBit('plc'):
                if err.checkBit('gsmUsb'):                  # CHECK IF GSM IS DISCONNECTED FROM RPi
                        print ("\n\t\tERROR: PLC & GSM disconnected !!\n\n")
                else:
                    print ('\n\n\tERROR: PLC DISCONNECTED !!\
                    PLEASE REBOOT\n\n')

                time.sleep(5)
            else:
                print('s-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))

                try:
                    arg=self.delta.readData()
                    print("\n\n\tDATA READ FROM PLC!!\n\n")
                    
                    if err.checkBit('gsmUsb'):                  # CHECK IF GSM IS DISCONNECTED FROM RPi
                        self.db.insertDb(arg)
                        print ("\n\t\tERROR: GSM disconnected !!\
                        \n\t\tPACKET PUSHED TO BACKUP db\n\n")

                        time.sleep(1)
                    else:
                        self.gsm.gsmInit(arg,'live')
                except Exception as e:
                    print('Error, live_run: '+str(e))
            

            
            
            err.clearBit('boot')            #Bit boot is cleared for all packets except the 1st Live
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
            

