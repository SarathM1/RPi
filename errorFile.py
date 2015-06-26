class errorHandler():
    def __init__(self):
        self.code = 0
    def lookup(self,errType):
        return {
        'boot':1,
        'plc': 2,
        'gsmUsb': 3,
        'gsmConn':4,
        'gsmCpin':5,
        'gsmCsq':6,
        'gsmCreg':7,
        'gsmCgatt':8,
        'gsmCiicr':9,
        }.get(errType)

    def checkBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print(e)
            return None
        else:
            return (True if ( self.code &  mask) else False)
    def setBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print(e)
        else:
            self.code |= mask
    def clearBit(self,errType):
        try:
            mask = 1 << self.lookup(errType)
        except Exception as e:
            print (e)
        else:
            self.code &= (~mask)

        
        

#error = error()
#print error.checkBit('gsmUsb')