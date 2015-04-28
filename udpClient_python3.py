import serial
import time
import threading
import sqlite3
import random


class Sim900():
    def __init__ (self):
        self.obj = serial.Serial('/dev/ttyS0',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,1)
        self.db=database()
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

    def gsmInit(self,device,level,time,case='backfill'):
        #while True:
        self.sendAt('at')
        self.sendAt('at+cipclose')
        self.sendAt('ate0')
        self.sendAt('at+cpin?')
        self.sendAt('at+csq')
        self.sendAt('at+creg?')
        self.sendAt('at+cgatt?')
        self.sendAt('at+cipshut')
        status=self.sendAt('at+cstt="bsnlnet"')

        flag = self.sendAt('at+ciicr','OK','ERROR',20)
        self.sendAt('at+cifsr','.','ERROR')
        flag = self.sendAt('at+cipstart="UDP","52.74.18.53","50001"')
        if 'Error' in flag:
            self.db.insertDb(device,level,time)
            print('Error in gsmInit')
            pass
        else:
            self.sendAt('at+cipqsend=1')
            self.sendPacket(device,level,time,case)
            #break
        """if case != 'backfill':
            break"""

    def sendPacket(self,device,level,time,case ='backfill'):
        #flag='dummy value'              # Just to avoid error

        #while 'Error' not in flag:
        packet=device+';'+str(level)+';'+str(time)
        self.sendAt('at+cipsend','>','ERROR')
        self.obj.write(bytes(packet+'\x1A',encoding='ascii'))           # bytes(command+'\r\n',encoding='ascii')
        flag = self.checkStatus('DATA ACCEPT',';')
        
        if case != 'backfill':              # case!='backfill' => live
            if 'Error' in flag:             # Backup data if live sending fails
                print('\tLive : Failed!!')
                self.db.insertDb(device,level,time)
            else:
                print('\tLive : Success . .')
            #break
        elif case=='backfill':
            if flag=='success':    #Delete packet from database once backfill has send it to server succesfully
                print('backfill : Success . .')
                self.db.deleteDb('live',time,level)
            else:
                print('device = ',device)
                print('backfill : Failed!!')

        

class database():

    def db_init(self):
        conn = sqlite3.connect("/home/wa/Documents/RPi/backup.db")
        c=conn.cursor()
        try:
            c.execute("CREATE TABLE table1(device TEXT,level INT,time TEXT)")
            conn.close()
        except Exception as e:
            print(('db_init ERROR:'+str(e)))
            pass
        finally:
            conn.close()
    def fetchData(self):
        conn=sqlite3.connect("/home/wa/Documents/RPi/backup.db")
        c=conn.cursor()
        c.execute("SELECT * FROM table1 ORDER BY ROWID LIMIT 1")
        data=c.fetchone()
        conn.close()
        return data
    def insertDb(self,device,level,currentTime):
        conn=sqlite3.connect("/home/wa/Documents/RPi/backup.db")
        c=conn.cursor()
        c.execute("INSERT INTO table1 values(?,?,?)",( device,str(level),str(currentTime) ))
        conn.commit()
        conn.close()
    def deleteDb(self,device,time,level):
        conn=sqlite3.connect("/home/wa/Documents/RPi/backup.db")
        c=conn.cursor()
        sql = "DELETE FROM table1 WHERE device=? and time=? and level=?"
        c.execute(sql,[device,time,level])
        conn.commit()
        conn.close()

class backFill(threading.Thread):
    
    def __init__(self,event):
        threading.Thread.__init__(self)
        self.event = event
        self.db=database()
        self.gsm = Sim900()

    def run(self):
        i=1
        while True:
            self.event.wait()
            data = self.db.fetchData()
            if not data:
                print ('Database is empty')
                time.sleep(1)
            else:
                self.gsm.sendPacket('backfill',data[1],data[2],'backfill')
                time.sleep(1)

class live(threading.Thread):
    def __init__(self,event):
        
        
        threading.Thread.__init__(self)
        self.event = event
        self.gsm = Sim900()
    
    def run(self):
        
        while True:
            
            self.event.clear()             #One event occurs in live thread btw event.clear() and event.wait
            
            print('s-------------Live:' ,time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))
            
            device = 'live'
            level = random.randint(1,100)
            curTime = time.strftime('%d/%m/%Y %H:%M:%S',time.localtime())

            self.gsm.gsmInit(device,level,curTime,'live')
            print('e-------------Live: ',time.strftime('%d/%m/%Y %H:%M:%S',time.localtime()))
            
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
            

