import serial
import time

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

    def gsmInit(self,packet):
        while True:
            self.sendAt('ate0')
            self.sendAt('at+cpin?')
            self.sendAt('at+csq')
            self.sendAt('at+creg?')
            self.sendAt('at+cgatt?')
            self.sendAt('at+cipshut')
            status=self.sendAt('at+cstt="bsnlnet"')

            flag = self.sendAt('at+ciicr','OK','ERROR',20)
            self.sendAt('at+cifsr','.','ERROR')
            flag = self.sendAt('at+cipstart="UDP","52.74.157.254","50001"')
            if 'Error' in flag:
                print 'Error in gsmInit'
                pass
            else:
                self.sendAt('at+cipqsend=1')
                raw_input()
                self.sendPacket(packet)

    def sendPacket(self,packet):
        flag='dummy value'              # Just to avoid error  
        while 'Error' not in flag:
            self.sendAt('at+cipsend','>','ERROR')
            self.obj.write('packet;packet;packet'+'\x1A')
            flag = self.checkStatus('DATA ACCEPT',';')
        self.sendAt('at+cipclose')
if __name__ == '__main__':
    gsm=Sim900()
    gsm.gsmInit()
            
      