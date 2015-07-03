import pymysql
from datetime import datetime as dt

conn = pymysql.connect(host="localhost", user="root", passwd="aaggss", db="dredger")
cur = conn.cursor()
#FUll- PAth : sqlite:////tmp/tutorial/joindemo.db
# sudo apt-get install python3-mysql.connector


class database_backup():
	def insertDb(self,arg,error_other,error_gsm,error_gsm_timeout):
		try:
			cur.execute("INSERT INTO backfill (dredger_name,\
				time,\
				storage_tank_level,\
				storage_tank_cap,\
				service_tank_level,\
				service_tank_cap,\
				flowmeter_1_in,\
				flowmeter_1_out,\
				engine_1_status,\
				flowmeter_2_in ,\
				flowmeter_2_out,\
				engine_2_status,\
				error_other,\
				error_gsm)\
			 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);",
			 	[arg['dredger_name'],
			 	arg['time'],
			 	arg['storage_tank_level'],
			 	arg['storage_tank_cap'],
			 	arg['service_tank_level'],
			 	arg['service_tank_cap'],
			 	arg['flowmeter_1_in'],
			 	arg['flowmeter_1_out'],
			 	arg['engine_1_status'],
			 	arg['flowmeter_2_in'],
			 	arg['flowmeter_2_out'],
			 	arg['engine_2_status'],
			 	error_other,
			 	error_gsm,
			 	error_gsm_timeout])
			conn.commit()

		except Exception as e:
			print ('insertDb: '+str(e))
			
	def deleteDb(self,arg):
		try:
			cur.execute("DELETE FROM backfill where time = %s",[arg['time']])
			conn.commit()
		except Exception as e:
			print ('deleteDb: '+str(e))
	def fetchData(self):
		try:
			cur.execute("SELECT * FROM backfill order by time")
			row = cur.fetchone()
			
			if not row:
				return None  # If database is empty
			else:
				dictRow={}
				dictRow['dredger_name']        = row[1]
				dictRow['time']                 = row[2]
				dictRow['storage_tank_level']   = row[3]
				dictRow['storage_tank_cap']     = row[4]
				dictRow['service_tank_level']   = row[5]
				dictRow['service_tank_cap']     = row[6]
				dictRow['flowmeter_1_in']       = row[7]
				dictRow['flowmeter_1_out']      = row[8]
				dictRow['engine_1_status']      = row[9]
				dictRow['flowmeter_2_in']       = row[10]
				dictRow['flowmeter_2_out']      = row[11]
				dictRow['engine_2_status']      = row[12]
				dictRow['error_other']			= row[13]
				dictRow['error_gsm']			= row[13]
				dictRow['error_gsm_timeout']	= row[14]
				return dictRow
		except Exception as e:
			print ('fetchData: '+str(e))

