
#!/usr/bin/python3
import serial
import time
import threading
from backfill import database_backup
from errorFile import errorHandler      # Import from local file errorFile 
import minimalmodbus
"""
Install Library Minimalmodbus 0.6, 
there is error in using MODE_ASCII in python 3 for Minimalmodbus 0.5 library

Source: http://sourceforge.net/projects/minimalmodbus/?source=typ_redirect
Commands:       
                cd /home/wa/Music/MinimalModbus-0.6
                sudo python3 setup.py install
"""


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
        except Exception as e:
            print('plc_init: '+str(e))
            err.setBit('plc')
            print ('Error in PLC ? : ',err.checkBit('plc'))
    def readData(self):
        cap=['Close','Open']
        status=['Off','On']
        arg={}

        try:
            
            if err.checkBit('plc'):       # If PLC is disconnected

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

        except Exception as e:
                print('PLC_read_data: ',str(e))

        return arg

class Sim900():
    def __init__ (self):
        try:
            self.obj = serial.Serial('/dev/port2',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,1)
            
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
        #while True:
        
        self.sendAt('at')
        self.sendAt('at+cipclose')
        self.sendAt('ate0')
        self.sendAt('at+cpin?')
        self.sendAt('at+csq')
        self.sendAt('at+creg?')
        self.sendAt('at+cgatt?')
        self.sendAt('at+cipshut')
        status=self.sendAt('at+cstt="internet"')

        flag = self.sendAt('at+ciicr','OK','ERROR',20)
        self.sendAt('at+cifsr','.','ERROR')

        flag = self.sendAt('at+cipstart="TCP","54.169.57.106","5000"','CONNECT OK','FAIL')
        self.checkStatus('ACK_FROM_SERVER','ERROR',3)
        if 'Error' in flag:
            self.db.insertDb(arg)
            print('Error in gsmInit')
            pass
        else:
            #self.sendAt('at+cipqsend=1')
            self.sendPacket(arg,case)
            #break
        
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

        
        self.sendAt('at+cipsend','>','ERROR',5)
        #self.obj.write(bytes(packet+'\n\r'+'\x1A',encoding='ascii'))           # bytes(command+'\r\n',encoding='ascii')
        self.obj.write(bytes(packet+'\x0A\x0D\x0A\x0D\x1A',encoding='ascii'))
        flag = self.checkStatus('SEND OK','ERROR',3)

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
        #self.event = event
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
                #self.gsm.sendPacket(arg,'backfill',self.event)
                self.gsm.sendPacket(arg,'backfill')
                time.sleep(0.5)
            backfillEvent.set()
class live(threading.Thread):
    def __init__(self,event):
        self.delta=plc()
        threading.Thread.__init__(self)
        #self.event = event
        self.gsm = Sim900()
    
    def run(self):
        
        while True:
            
            #self.event.clear()             #One event occurs in live thread btw event.clear() and event.wait
            event.clear()
            backfillEvent.wait()
            print('s-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))
            
            try:
                arg=self.delta.readData()
                print("\n\n\tDATA READ FROM PLC!!\n\n")
                self.gsm.gsmInit(arg,'live')
            except Exception as e:
                print('Error, live_run: '+str(e))
            

            
            print('e-------------Live: ',time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))
            
            #self.event.set()  
            event.set()
            
            time.sleep(10)                   #backfill runs for 10 sec's
            
def main():
    t1 = backFill(event)
    t2 = live(event)
    t1.start()
    t2.start()

    

if __name__ == '__main__':
    event = threading.Event()
    backfillEvent = threading.Event()
    backfillEvent.set()
    err = errorHandler()           # import from file errorFile.py
    main()
            

