#!/usr/bin/python3

import minimalmodbus
import serial
import time



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
            msg = self.serialPort.read(100).decode('ascii').strip()
            if msg:
                return msg
    
    def __del__(self):
        self.serialPort.close()
        
                

if __name__ == '__main__':
    while True:
        try:
            instrument = minimalmodbus.Instrument('/dev/ttyUSB0',1)
            instrument.serial.baudrate = 9600
            instrument.serial.bytesize = 7
            instrument.serial.parity = serial.PARITY_EVEN
            instrument.serial.stopbits = 1
            instrument.serial.timeout = 0.1
            instrument.mode = minimalmodbus.MODE_ASCII


            while True:
                level = instrument.read_register(4096) #404097 is 4097-1 in python
                if level==65535:
                    level=0
                time.sleep(0.5)
                print (level)
        except Exception as e:
            print(e)
            time.sleep(1)
    
   
        
