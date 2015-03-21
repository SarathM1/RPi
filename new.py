#!/usr/bin/python3

import minimalmodbus
import serial
import time
import logging
import sqlite3
import threading


class Sim900(object):
    def __init__ (self,port,baud=9600,bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stop=serial.STOPBITS_ONE, timeout=1):
        self.serialPort = serial.Serial(port,baud,bytesize,parity,stop,timeout)

    def sendAtCommand(self,command):
        self.serialPort.write(bytes(command+'\r\n',encoding='ascii'))
        self.status =  self.readCommandResponse()
        return self.status

    def readCommandResponse(self):
        time.sleep(0.25)
        while True:
            try:

                msg = self.serialPort.read(100).decode('ascii').strip()
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

        #conn = sqlite3.connect("backup.db")
        conn1 = sqlite3.connect("backup.db")
        c=conn1.cursor()
        c.execute("SELECT * FROM table1 ORDER BY ROWID")
        data = c.fetchall()
        conn1.close()
        for item in data:
            #lock.wait()
            print ('in thread: ', item[0],item[1],item[2])
            conn1 = sqlite3.connect("backup.db")
            c=conn1.cursor()
            sql = "DELETE FROM table1 WHERE time=? and level=?"
            c.execute(sql,[item[2],item[1]])
            conn1.commit()
            conn1.close()

            """try:
                    modem = Sim900('/dev/ttyS0')
                    try:
                        modem.sendAtCommand('AT')
                        print (modem.status)
                    except Exception as e:
                        print ('at:'+str(e))
                    try:
                        modem.sendAtCommand('AT+CREG?')
                        print (modem.status)
                    except Exception as e:
                        print ('at+creg?:'+str(e))
                    try:
           
                        modem.sendAtCommand('AT+CGATT=1')
                        print (modem.status)
                    except Exception as e:
                        print ('at+cgatt=1:'+str(e))    
                    modem.sendAtCommand('AT+CSTT="www"')
                    print (modem.status)
                    modem.sendAtCommand('AT+CIICR')
                    print (modem.status)
                    modem.sendAtCommand('AT+CIFSR')
                    print (modem.status)
            except Exception as e:
                print(e)"""


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
        try:

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
            try:
                modem = Sim900('/dev/ttyS0')
                try:
                    modem.sendAtCommand('AT')
                    print (modem.status)
                except Exception as e:
                    print ('at:'+str(e))
                try:
                    modem.sendAtCommand('AT+CREG?')
                    print (modem.status)
                except Exception as e:
                    print ('at+creg?:'+str(e))
                try:
       
                    modem.sendAtCommand('AT+CGATT=1')
                    print (modem.status)
                except Exception as e:
                    print ('at+cgatt=1:'+str(e))    
                modem.sendAtCommand('AT+CSTT="www"')
                print (modem.status)
                modem.sendAtCommand('AT+CIICR')
                print (modem.status)
                modem.sendAtCommand('AT+CIFSR')
                print (modem.status)
                modem.sendAtCommand('AT+CCLK')
                print (modem.status)
                
            except Exception as e:
                print('whole:'+str(e))
            level='1'

            e = 'ERROR'
            device = 'DGD001'
            while True:
                lock.clear()
                currentTime = time.strftime('%d/%m/%Y %H:%M:%S',time.gmtime())
                level=30
                """packet = device + ';' + str(level) + ';' + str(currentTime)+'\x1A'
                                                                print ('gmtime: ' + currentTime)"""

                
                modem.sendAtCommand('AT+CIPSTART="UDP","52.74.91.12","50001"')
                print (modem.status)

                if e in str(bytes(str(modem.status),'UTF-8')) :
                    print ('Error here')
                    raise serial.SerialException

                modem.sendAtCommand('AT+CIPSEND')
                
                """try:
                    #level = instrument.read_register(4105)
                    
                except Exception as e:
                    print (e)"""
                #level='2'
                
                currentTime = time.strftime('%d/%m/%Y %H:%M:%S',time.gmtime())
                packet = device + ';' + str(level) + ';' + str(currentTime)+'\x1A'
                print ('gmtime: ' + currentTime)
                modem.sendAtCommand(packet)
                print (modem.status)
                modem.sendAtCommand('AT+CIPCLOSE')
                #time.sleep(1)
                print(packet)
                print('----------------------------------------------------')
                lock.set()
                time.sleep(5)
                level = str(int(level)+1)


        except serial.SerialException as e:
            print (e)
            print (device,str(level),str(currentTime))
            #c.execute("INSERT INTO table1 values(?,?,?)",(device,str(level),str(currentTime)))
            c.execute("INSERT INTO table1 values(?,?,?)",( device,str(level),str(currentTime) ))
            conn2.commit()
            print('\nProgram aborted because there is error in opening the serial port.\n' )
            continue
        break



