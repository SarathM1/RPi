"""
Takes error_code as input and prints all the errors that has occured
based on the bits that are set
"""
class errorHandler():
    def lookup(self,errType):
        return {
        0:'boot',
        1:'plcUsb',
        2:'gsmUsb',
        3:'gsmConn',
        4:'gsmCpin',
        5:'gsmCsq',
        6:'gsmCreg',
        7:'gsmCgatt',
        8:'gsmCiicr',
        9:'plcComm',
        10:'serverAck',
        }.get(errType)

    def checkBit(self,errType,code):
        try:
            mask = 1 << errType
        except Exception as e:
            print('checkBit: ',e,errType)
            return None
        else:
            return (True if ( code &  mask) else False)

obj = errorHandler()
code = input("Enter the error code: ")
code = int(code)
for i in range(11):
	if obj.checkBit(i,code):
		print (obj.lookup(i))
