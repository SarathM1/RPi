import sqlite3
#conn = sqlite3.connect('./backfill.db',check_same_thread=False)
conn = sqlite3.connect('../backfill.db',check_same_thread=False)
cur = conn.cursor()


def table_create():
     cur.execute('''CREATE TABLE backfill(id INTEGER PRIMARY KEY AUTOINCREMENT,\
          dredger_name VARCHAR(15),\
          time DATETIME,\
          storage_tank_level INTEGER,\
          storage_tank_cap VARCHAR(5),\
          service_tank_level INTEGER,\
          service_tank_cap VARCHAR(5),\
          flowmeter_1_in INTEGER,\
          flowmeter_1_out INTEGER,\
          engine_1_status VARCHAR(5),\
          flowmeter_2_in INTEGER,\
          flowmeter_2_out INTEGER,\
          engine_2_status VARCHAR(5),\
          error_gsm VARCHAR(20),\
          error_main VARCHAR(20),\
          error_timeout VARCHAR(20),\
          error_unknown VARCHAR(20)\
          )''')
          
     

table_create()
