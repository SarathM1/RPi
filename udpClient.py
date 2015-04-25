import serial
import time
import threading
import sqlite3



class Sim900():
    def __init__ (self):
        self.obj = serial.Serial('/dev/ttyS0',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,1)
    
    def sendAt(self,command,success='OK',error='ERROR',wait=1):
        """
        Function to send AT commands
        to GSM Module
        """
        
        """if event!=0:                                # To avoid at commands being send from thread when live() is active
        while(event.is_set()==False):
            print event.is_set(),event
            time.sleep(1)"""
                #pass
        
        print '{0:20}'.format(command),
        code=command + '\r\n'
        self.obj.write(code)
        time.sleep(0.25)
        
        status=self.checkStatus(success,error,wait)
        return status

    def checkStatus(self,success='OK',error='ERROR',wait=1):
        """
        Function to wait and respond for Replies from modem for each
        AT command sent to it 
        """
        status = self.obj.read(100).strip()
        
        
        cntr=1                      # Timeout in secs
        while len(status)==0:           
            
            if cntr>wait:
                print '\n\tError, Time out, cntr = '+str(cntr)+'\n'
                return 'connError'
            cntr=cntr+1
            
            status = self.obj.read(100)
            time.sleep(1)
            if wait>1:         # If waitin for more than 5 sec display count
                print '\n\t'+str(cntr)

        
        #print '\t((('+status+')))'
        
        

        string=status.split('\n')
        string = ''.join(string)
        string = string.replace('\r',' ').replace(',,','; ')


        
        if success in status:
            #print '\t\t',
            print '{0:20} ==> {1:50}'.format('success',string)
            return 'success'  # success => AT Command sent
        elif error in status:
            print '{0:20} ==> {1:50}'.format('Error',string)
            return 'sendError'
        else:
            print '{0:20} ==> {1:50}'.format('Other',string)
            return 'other'

    def sendPacket(self,packet):
        #while True:
        print '------------------------'
        self.sendAt('ate0')
        self.sendAt('at+cpin?')
        self.sendAt('at+csq')
        self.sendAt('at+creg?')
        self.sendAt('at+cgatt?')
        self.sendAt('at+cipshut')
        status=self.sendAt('at+cstt="bsnlnet"')
        if 'connError' in status:
            flag='Error'
            pass
        else:
            flag = self.sendAt('at+ciicr','OK','ERROR',20)

        #if 'success' in flag:           # Skip the rest if sendError or connError
        self.sendAt('at+cifsr','.','ERROR')
        flag = self.sendAt('at+cipstart="UDP","52.74.106.150","50001"')   # Warning!! Enter correct IP address and Port, 50001 -UDP,50003-TCP
        #print 'flag = '+flag    # flag should be error if reply is CONNECT FAIL
        self.sendAt('at+cipsend','>','ERROR')
        self.obj.write('packet;packet;packet'+'\x1A')
        self.checkStatus('SEND OK','ERROR')
        self.sendAt('at+cipclose')
            
        #else:
        #self.sendAt('at+cipclose')

class database():

    def db_init(self):
        conn = sqlite3.connect("/home/wa/Documents/RPi/backup.db")
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

class backFill(threading.Thread):
    
    def __init__(self,event):
        threading.Thread.__init__(self)
        self.event = event
        self.db=database()
        

    def run(self):
        i=1
        while True:
            self.event.wait()
            print 'In backfill,i = ',i
            i=i+1            
            time.sleep(1)

class live(threading.Thread):
    def __init__(self,event):
        
        
        threading.Thread.__init__(self)
        self.db=database()
        self.event = event
        self.level='0'
        self.device = 'live'
        
        self.gsm = Sim900()
    
    def run(self):
        
        while True:
            
            self.event.clear()             #One event occurs in live thread btw event.clear() and event.wait
            
            print 's-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())
            packet='live;2;3'
            self.gsm.sendPacket(packet)
            print 'e-------------Live: ',time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())
            
            self.event.set()  
            
            time.sleep(10)                   #backfill runs for 10 sec's
            
def main():
    db=database()
    db.db_init()
    event = threading.Event()

    t1 = backFill(event)
    t2 = live(event)
    t1.start()
    t2.start()

    

if __name__ == '__main__':
    main()
            

