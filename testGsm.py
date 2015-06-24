import serial

obj = serial.Serial('/dev/port2',9600,serial.EIGHTBITS,serial.PARITY_NONE,serial.STOPBITS_ONE,1)

def sendAt(command):
	print(command)
	obj.write(bytes(command+'\r\n',encoding='ascii'))
	input()

while True:
	sendAt('at')
	sendAt('at+cipclose')
	sendAt('at+cpin?')
	sendAt('at+csq')
	sendAt('at+creg?')
	sendAt('at+cgatt?')
	sendAt('at+cipshut')
	sendAt('at+cstt="internet"')
	sendAt('at+ciicr')
	sendAt('at+cifsr')
	#sendAt('at+cipstart="udp","52.74.187.97","50001"')
	sendAt('at+cipstart="tcp","52.74.78.20","5000"')
	sendAt('at+cipstatus')
	sendAt('at+cipsend')
	obj.write(bytes('packet'+'\x0A\x0D\x0A\x0D\x1A',encoding='ascii'))
	input()
        