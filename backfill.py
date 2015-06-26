from sqlalchemy import *
from datetime import datetime as dt

db = create_engine('mysql+mysqlconnector://admin:aaggss@localhost/dredger')
#FUll- PAth : sqlite:////tmp/tutorial/joindemo.db
# sudo apt-get install python3-mysql.connector


metadata = MetaData(db)


backfill = Table('backfill', metadata, autoload=True)




class database_backup():
	def insertDb(self,arg):
		try:
			i = backfill.insert()
			i.execute(dredger_name = arg['dredger_name'],
			time                = arg['time'],					
			storage_tank_level  = arg['storage_tank_level'],
			storage_tank_cap    = arg['storage_tank_cap'],
			service_tank_level  = arg['service_tank_level'],
			service_tank_cap    = arg['service_tank_cap'],
			flowmeter_1_in      = arg['flowmeter_1_in'],
			flowmeter_1_out     = arg['flowmeter_1_out'],
			engine_1_status     = arg['engine_1_status'],
			flowmeter_2_in      = arg['flowmeter_2_in'],
			flowmeter_2_out     = arg['flowmeter_2_out'],
			engine_2_status     = arg['engine_2_status'],
			error_code 			= arg['error_code'],

			)
		except Exception as e:
			print ('insertDb: '+str(e))
			
	def deleteDb(self,arg):
		try:
			d = backfill.delete(backfill.c.time == arg['time'])
			d.execute()
		except Exception as e:
			print ('deleteDb: '+str(e))
	def fetchData(self):
		try:
			s = backfill.select().order_by(desc(backfill.c.time))
			e = s.execute()
			row = e.fetchone()
			if not row:
				return None  # If database is empty
			else:
				dictRow={}
				dictRow['dredger_name']        = row.dredger_name
				dictRow['time']                 = row.time
				dictRow['storage_tank_level']   = row.storage_tank_level
				dictRow['storage_tank_cap']     = row.storage_tank_cap
				dictRow['service_tank_level']   = row.service_tank_level
				dictRow['service_tank_cap']     = row.service_tank_cap
				dictRow['flowmeter_1_in']       = row.flowmeter_1_in
				dictRow['flowmeter_1_out']      = row.flowmeter_1_out
				dictRow['engine_1_status']      = row.engine_1_status
				dictRow['flowmeter_2_in']       = row.flowmeter_2_in
				dictRow['flowmeter_2_out']      = row.flowmeter_2_out
				dictRow['engine_2_status']      = row.engine_2_status
				dictRow['error_code']			= row.error_code
				return dictRow
		except Exception as e:
			#flash('insertDb: '+str(e))
			print ('fetchData: '+str(e))

