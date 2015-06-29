class errorHandler():
    def __init__(self):
        self.code = 0
    def lookup(self,errType):
        return {
        'boot':0,
        'plcUsb': 1,
        'gsmUsb': 2,
        'gsmConn':3,
        'gsmCpin':4,
        'gsmCsq':5,
        'gsmCreg':6,
        'gsmCgatt':7,
        'gsmCiicr':8,
        'plcComm':9,
        'serverAck':10,
        }.get(errType)

    def checkBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print('checkBit: ',e,errType)
            return None
        else:
            return (True if ( self.code &  mask) else False)
    def setBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print('setBit: ',e,errType)
        else:
            self.code |= mask
    def clearBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print ('clearBit',e,errType)
        else:
            self.code &= (~mask)

        
        

#error = error()
#print error.checkBit('gsmUsb')