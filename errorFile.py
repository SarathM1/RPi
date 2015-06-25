class errorHandler():
    def __init__(self):
        self.code = 8
    def lookup(self,errType):
        return {
        'boot':1,
        'plc': 2,
        'gsmUsb': 3,
        'gsmCpin':4,
        'gsmCsq':5,
        'gsmCreg':6,
        'gsmCgatt':7,
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