class errorHandlerGsm():
    def __init__(self):
        self.code = 0
    def lookup(self,errType):
        return {
        'at+ciicr'      :0,
        'at+cipstart'   :1,
        'at+cipclose'   :2,
        'at+cgatt?'     :3,
        'at+cstt'       :4,
        'at+csq'        :5,
        'at+cpin?'      :6,
        'at+creg?'      :7,
        'at+cipshut'    :8,
        'at+cstt'       :9,
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
            print("\n\t\t\tGSM: setBit('",errType,"')\n\n")
    
    def clearBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print ('GSM: clearBit',e,errType)
        else:
            self.code &= (~mask)
            print("\n\t\t\tGSM: clearBit('",errType,"')\n\n") 


class errorHandlerMain():
    def __init__(self):
        self.code = 0
    def lookup(self,errType):
        return {
        'boot'      :0,
        'packet'    :1,
        'gsmInit'   :2,
        'gsmSend'   :3,
        'plcUsb'    :5,
        'gsmUsb'    :6,
        'plcComm'   :7,
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
            print("\n\t\t\tMAIN: setBit('",errType,"')\n\n")
    
    def clearBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print ('MAIN: clearBit',e,errType)
        else:
            self.code &= (~mask)
            print("\n\t\t\tMAIN: clearBit('",errType,"')\n\n") 
        
class errorHandlerTimeout():
    def __init__(self):
        self.code = 0
    def lookup(self,errType):
        return {
        'at+ciicr'      :0,
        'at+cipstart'   :1,
        'at+cipclose'   :2,
        'at+cgatt?'     :3,
        'at+cstt'       :4,
        'at+csq'        :5,
        'at+cpin?'      :6,
        'at+creg?'      :7,
        'at+cipshut'    :8,
        'at+cstt'       :9,
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
            print("\n\t\t\tTIMEOUT: setBit('",errType,"')\n\n")
    
    def clearBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print ('TIMEOUT: clearBit',e,errType)
        else:
            self.code &= (~mask)
            print("\n\t\t\tTIMEOUT: clearBit('",errType,"')\n\n") 

class errorHandlerUnknown():
    def __init__(self):
        self.code = 0
    def lookup(self,errType):
        return {
        'at+ciicr'      :0,
        'at+cipstart'   :1,
        'at+cipclose'   :2,
        'at+cgatt?'     :3,
        'at+cstt'       :4,
        'at+csq'        :5,
        'at+cpin?'      :6,
        'at+creg?'      :7,
        'at+cipshut'    :8,
        'at+cstt'       :9,
        'at+cifsr'      :10,
        'ate0'          :11,
        'at'            :12,
        'live'          :13,
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
            print("\n\t\t\tUNKNOWN: setBit('",errType,"')\n\n")
    
    def clearBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print ('UNKNOWN: clearBit',e,errType)
        else:
            self.code &= (~mask)
            print("\n\t\t\tUNKNOWN: clearBit('",errType,"')\n\n") 