"""
Takes error_code as input and prints all the errors that has occured
based on the bits that are set
"""
class errorHandler():
    def lookup(self,errType):
        return {
        0:'First boot',
        1:'PLC 	-->	Disconnected from USB Port',
        2:'GSM 	-->	Modem Disconnected from USB Ported',
        3:'AT 	--> CONNECT FAIL',
        4:'AT 	-->	Pin Code Error',
        5:'AT 	-->	Signal Quality Error',
        6:'AT 	-->	Sim Registration Error',
        7:'AT 	-->	GPRS Attached error',
        8:'AT 	-->	CIICR',
        9:'PLC	-->	Communication Error(No Answer)',
        10:'SERVER	-->	No ACK From SERVER',
        }.get(errType)

    def checkBit(self,errType,code):
        try:
            mask = 1 << errType
        except Exception as e:
            print('checkBit: ',e,errType)
            return None
        else:
            return (True if ( code &  mask) else False)

while True:
	obj = errorHandler()
	code = input("\nEnter the error code: ")
	code = int(code)
	for i in range(11):
		if obj.checkBit(i,code):
			print (obj.lookup(i))
