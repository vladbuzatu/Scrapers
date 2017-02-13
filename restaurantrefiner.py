# -*- coding: utf-8 -*-

# refine data in database

import MySQLdb

db = MySQLdb.connect("localhost", "root", "admin", "gw_db")
cursor = db.cursor()

query = """Select * from utilityapp_restaurant"""
cursor.execute(query)

for c in cursor:
	if c[0].find("';") != -1:
		print c[0]
		x = c[0][:c[0].find("';")] + "'" +  c[0][c[0].find("';")+2:]
		query = """UPDATE utilityapp_restaurant SET name = %s WHERE name =  %s"""
		cursor.execute(query, (x,c[0]))
		print x
		db.commit()