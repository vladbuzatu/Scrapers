# Get latitude and longitude coordinates for all the venues in the database

import urllib2
import MySQLdb
import json

db = MySQLdb.connect("localhost", "root", "admin", "gw_db")

cursor = db.cursor()
curs = db.cursor()
cursor.execute("SELECT address, venueID FROM utilityapp_venue")


for c in cursor:
	address = c[0].replace(" ", "+")
	print c
	url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s" % address
	response = urllib2.urlopen(url)
	jsongeocode = response.read()
	x = json.loads(jsongeocode)
	if x['status'] == "OK":
		lat = x['results'][len(x['results']) - 1]['geometry']['location']['lat']
		lng = x['results'][len(x['results']) - 1]['geometry']['location']['lng']
		print lat
		print lng
		curs.execute("""UPDATE utilityapp_venue SET latitude = %f, longitude = %f WHERE venueID =  %s"""%(lat, lng, c[1]))
		print c[1] + "--------------------------------------------UPDATED!"
	else:
		print c[1] + "--------------------------------------------NOT UPDATED!!!"

db.commit()
db.close()