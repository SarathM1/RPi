class errorHandlerGsm():
    def __init__(self):
        self.code = 0x00
    def lookup(self,errType):
        return {
        'at+ciicr'      :0,
        'at+cipstart="TCP","52.74.77.168","5000"'   :1,
        'at+cipsend'    :2,
        'at+cipclose=1'   :3,
        'at+cgatt?'     :4,
        'at+cstt="internet"':5,
        'at+csq'        :6,
        'at+cpin?'      :7,
        'at+creg?'      :8,
        'at+cipshut'    :9,
        'at+cifsr'      :10,
        'ate0'          :11,
        'at'            :12,
        }.get(errType)

    def checkBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print('GSM: checkBit: ',e,errType)
            return None
        else:
            return (True if ( self.code &  mask) else False)
    
    def setBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print('GSM: setBit: ',e,errType)
        else:
            self.code |= mask
            #print("\n\t\t\tGSM: setBit('",errType,"')\n\n")
    
    def clearBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print ('GSM: clearBit',e,errType)
        else:
            self.code &= (~mask)
            #print("\n\t\t\tGSM: clearBit('",errType,"')\n\n") 


class errorHandlerMain():
    def __init__(self):
        self.code = 0x00
    def lookup(self,errType):
        return {
        'boot'      :0,
        'gsmInit'   :1,
        'liveSend'  :2,
        'plcUsb'    :3,
        'gsmUsb'    :4,
        'plcComm'   :5,
        }.get(errType)

    def checkBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print('MAIN: checkBit: ',e,errType)
            return None
        else:
            return (True if ( self.code &  mask) else False)
    
    def setBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print('MAIN: setBit: ',e,errType)
        else:
            self.code |= mask
            #print("\n\t\t\tMAIN: setBit('",errType,"')\n\n")
    
    def clearBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print ('MAIN: clearBit',e,errType)
        else:
            self.code &= (~mask)
            #print("\n\t\t\tMAIN: clearBit('",errType,"')\n\n") 
        
class errorHandlerTimeout():
    def __init__(self):
        self.code = 0x00
    def lookup(self,errType):
        return {
        'at+ciicr'      :0,
        'at+cipstart="TCP","52.74.77.168","5000"':1,
        'at+cipsend'    :2,
        'at+cipclose=1'   :3,
        'at+cgatt?'     :4,
        'at+cstt="internet"':5,
        'at+csq'        :6,
        'at+cpin?'      :7,
        'at+creg?'      :8,
        'at+cipshut'    :9,
        'at+cifsr'      :10,
        'ate0'          :11,
        'at'            :12,
        }.get(errType)

    def checkBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print('TIMEOUT: checkBit: ',e,errType)
            return None
        else:
            return (True if ( self.code &  mask) else False)
    
    def setBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print('TIMEOUT: setBit: ',e,errType)
        else:
            self.code |= mask
            #print("\n\t\t\tTIMEOUT: setBit('",errType,"')\n\n")
    
    def clearBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print ('TIMEOUT: clearBit',e,errType)
        else:
            self.code &= (~mask)
            #print("\n\t\t\tTIMEOUT: clearBit('",errType,"')\n\n") 

class errorHandlerUnknown():
    def __init__(self):
        self.code = 0x00
    def lookup(self,errType):
        return {
        'at+ciicr'                                  :0,
        'at+cipstart="TCP","52.74.77.168","5000"'  :1,
        'at+cipsend'                                :2,
        'at+cipclose=1'                               :3,
        'at+cgatt?'                                 :4,
        'at+cstt="internet"'                        :5,
        'at+csq'        :6,
        'at+cpin?'      :7,
        'at+creg?'      :8,
        'at+cipshut'    :9,
        'at+cifsr'      :10,
        'ate0'          :11,
        'at'            :12,
        'liveSend'      :13,
        }.get(errType)

    def checkBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print('UNKNOWN: checkBit: ',e,errType)
            return None
        else:
            return (True if ( self.code &  mask) else False)
    
    def setBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print('UNKNOWN: setBit: ',e,errType)
        else:
            self.code |= mask
            #print("\n\t\t\tUNKNOWN: setBit('",errType,"')\n\n")
    
    def clearBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print ('UNKNOWN: clearBit',e,errType)
        else:
            self.code &= (~mask)
            #print("\n\t\t\tUNKNOWN: clearBit('",errType,"')\n\n") 