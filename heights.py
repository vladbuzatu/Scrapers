import urllib2
import MySQLdb
import json

db = MySQLdb.connect("localhost", "root", "admin", "gw_db")
cursor = db.cursor()

heights = []
next = False

with open('eventIDheights.txt') as datafile:
	for f in datafile:
		if f.find("eventID") != -1:
			evID = f[16:20]
			next = True
		elif next == True:
			next = False
			heights.append({"eventID": evID, "height": f[20:24]})

for h in heights:
	cursor.execute("""UPDATE utilityapp_event SET height = %d WHERE eventID =  %s"""%(int(h['height']), h['eventID']))

db.commit()