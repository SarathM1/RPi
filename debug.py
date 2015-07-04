"""
Takes error_code as input and prints all the errors that has occured
based on the bits that are set
"""
class errorHandlerGsm():
		
	def lookup(self,errType):
		return {
		0       :'at+ciicr',
		1       :'at+cipstart="TCP","52.74.229.218","5000"',
		2       :'at+cipsend',
		3       :'at+cipclose',
		4       :'at+cgatt?',
		5       :'at+cstt="internet"',
		6       :'at+csq',
		7       :'at+cpin?',
		8       :'at+creg?',
		9       :'at+cipshut',
		10      :'at+cifsr',
		11      :'ate0',
		12      :'at',
		}.get(errType)


	def checkBit(self,errType,code):
		try:
			mask = 1 << errType
		except Exception as e:
			print('GSM: checkBit: ',e,errType)
			return None
		else:
			return (True if ( code &  mask) else False)
	
	

class errorHandlerMain():
		
	def lookup(self,errType):
		return {
		0:'boot',
		1:'gsmInit',
		2:'liveSend',
		3:'plcUsb',
		4:'gsmUsb',
		5:'plcComm',
		}.get(errType)
        
	def checkBit(self,errType,code):
		try:
			mask = 1 << errType
		except Exception as e:
			print('MAIN: checkBit: ',e,errType)
			return None
		else:
			return (True if ( code &  mask) else False)
	
		
class errorHandlerTimeout():
		
	def lookup(self,errType):
		return {
		0:'at+ciicr',
		1:'at+cipstart="TCP","52.74.229.218","5000"',
		2:'at+cipsend',
		3:'at+cipclose',
		4:'at+cgatt?',
		5:'at+cstt="internet"',
		6:'at+csq',
		7:'at+cpin?',
		8:'at+creg?',
		9:'at+cipshut',
		10:'at+cifsr',
		11:'ate0',
		12:'at',
		}.get(errType)


	def checkBit(self,errType,code):
		try:
			mask = 1 << errType
		except Exception as e:
			print('TIMEOUT: checkBit: ',e,errType)
			return None
		else:
			return (True if ( code &  mask) else False)
	
	

class errorHandlerUnknown():
	
	def lookup(self,errType):
		return {
		0:'at+ciicr',
		1:'at+cipstart="TCP","52.74.229.218","5000"',
		2:'at+cipsend',
		3:'at+cipclose',
		4:'at+cgatt?',
		5:'at+cstt="internet"',
		6:'at+csq',
		7:'at+cpin?',
		8:'at+creg?',
		9:'at+cipshut',
		10:'at+cifsr',
		11:'ate0',
		12:'at',
		13:'liveSend',
		}.get(errType)


        
	def checkBit(self,errType,code):
		try:
			mask = 1 << errType
		except Exception as e:
			print('UNKNOWN: checkBit: ',e,errType)
			return None
		else:
			return (True if ( code &  mask) else False)
	
	

while True:
	print '\n#########################################################\n'
	errGsm      = errorHandlerGsm()
	errMain     = errorHandlerMain()
	errTime     = errorHandlerTimeout()
	errUnknown  = errorHandlerUnknown()

	codeGsm     = raw_input("Enter the GSM error code: 0x")
	codeMain    = raw_input("Enter the MAIN error code: 0x")
	codeTime    = raw_input("Enter the TIME error code: 0x")
	codeUnknown = raw_input("Enter the UNKNOWN error code: 0x")
	
	codeGsm     = int(codeGsm,16)
	codeMain    = int(codeMain,16)
	codeTime    = int(codeTime,16)
	codeUnknown = int(codeUnknown,16)

	for i in range(13):
		if errGsm.checkBit(i,codeGsm):
			print ('{0:20} ==> {1:50}'.format('GSM',errGsm.lookup(i)))

	for i in range(8):
		if errGsm.checkBit(i,codeMain):
			print ('{0:20} ==> {1:50}'.format('MAIN',errMain.lookup(i)))
	
	for i in range(13):
		if errGsm.checkBit(i,codeTime):
			print ('{0:20} ==> {1:50}'.format('TIMEOUT',errTime.lookup(i)))
	
	for i in range(15):
		if errGsm.checkBit(i,codeUnknown):
			print ('\n{0:20} ==> {1:50}'.format('UNKNOWN',errUnknown.lookup(i)))
	

