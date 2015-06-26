from sqlalchemy import *
from sqlalchemy.orm import mapper

db = create_engine('mysql+mysqlconnector://admin:aaggss@localhost/dredger')
 #FUll- PAth : sqlite:////tmp/tutorial/joindemo.db
 # sudo apt-get install python3-mysql.connector

db.echo = True  					# Print SQL for each SQLAlchemy instruction
metadata = MetaData(db)





class backfill_manage():
    def table_create(self):
        backfill = Table('backfill', metadata,
        Column('id',Integer, primary_key=True),
        Column('dredger_name',String(25)),
        Column('time',DateTime,unique=True),  # If not unique then there will be logical errors
        Column('storage_tank_level',Integer),
        Column('storage_tank_cap',String(25)),
        Column('service_tank_level',Integer),
        Column('service_tank_cap',String(25)),
        Column('flowmeter_1_in',Integer),
        Column('flowmeter_1_out',Integer),
        Column('engine_1_status',String(25)),
        Column('flowmeter_2_in',Integer),
        Column('flowmeter_2_out',Integer),
        Column('engine_2_status',String(25)),
        )

        backfill.create()

