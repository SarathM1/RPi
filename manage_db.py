import pymysql
conn = pymysql.connect(host='127.0.0.1', user='root', passwd='aaggss',db='dredger')
cur = conn.cursor()


def table_create():
    cur.execute('CREATE TABLE backfill (id INTEGER NOT NULL AUTO_INCREMENT,\
     dredger_name VARCHAR(25),\
     time DATETIME,\
     storage_tank_level INTEGER,\
     storage_tank_cap VARCHAR(25),\
     service_tank_level INTEGER,\
     service_tank_cap VARCHAR(25),\
     flowmeter_1_in INTEGER,\
     flowmeter_1_out INTEGER,\
     engine_1_status VARCHAR(25),\
     flowmeter_2_in INTEGER,\
     flowmeter_2_out INTEGER,\
     engine_2_status VARCHAR(25),\
     error_other VARCHAR(25),\
     error_gsm VARCHAR(25),\
     error_gsm_timeout VARCHAR(25),\
     PRIMARY KEY (id),\
     UNIQUE (time))')

table_create()