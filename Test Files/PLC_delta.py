#!/usr/bin/python3

import minimalmodbus
import serial
from time import sleep
import datetime 


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
            instrument = minimalmodbus.Instrument('/dev/port1',2)
            #instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1, minimalmodbus.MODE_ASCII)
            instrument.serial.baudrate = 9600
            instrument.serial.bytesize = 7
            instrument.serial.parity = serial.PARITY_EVEN
            instrument.serial.stopbits = 1
            instrument.serial.timeout = 0.1
            instrument.mode = minimalmodbus.MODE_ASCII


            while True:
                #level = instrument.read_register(4096) #404097 is 4097-1 in python

                dreadger_name       = 'dreadger_name'
                time                = datetime.datetime.now()
                storage_tank_level  = instrument.read_register(4096)
                storage_tank_cap    = instrument.read_register(4104)
                service_tank_level  = instrument.read_register(4097)
                service_tank_cap    = instrument.read_register(4105)
                flowmeter_1_in      = instrument.read_register(4098)
                flowmeter_1_out     = instrument.read_register(4100)
                engine_1_status     = instrument.read_register(4106)
                flowmeter_2_in      = instrument.read_register(4103)
                flowmeter_2_out     = instrument.read_register(4101)
                engine_2_status     = instrument.read_register(4107)

                print('############################################################')
                print('{0:20} ==> {1:5}'.format('storage_tank_level',storage_tank_level))
                print('{0:20} ==> {1:5}'.format('storage_tank_cap',storage_tank_cap))
                print('{0:20} ==> {1:5}'.format('service_tank_level',service_tank_level))
                print('{0:20} ==> {1:5}'.format('service_tank_cap',service_tank_cap))
                print('{0:20} ==> {1:5}'.format('flowmeter_1_in',flowmeter_1_in))
                print('{0:20} ==> {1:5}'.format('flowmeter_1_out',flowmeter_1_out))
                print('{0:20} ==> {1:5}'.format('engine_1_status',engine_1_status))
                print('{0:20} ==> {1:5}'.format('flowmeter_2_in',flowmeter_2_in))
                print('{0:20} ==> {1:5}'.format('flowmeter_2_out',flowmeter_2_out))
                print('{0:20} ==> {1:5}'.format('engine_2_status',engine_2_status))
                print('############################################################')
                
                raw_input()
                #print (level)
        except Exception as e:
            print(e)
            sleep(1)
    
   
        
