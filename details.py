import urllib2
import MySQLdb
import json

db = MySQLdb.connect("localhost", "root", "admin", "gw_db")
cursor = db.cursor()
cursor2 = db.cursor()
cursor.execute("SELECT venueID, latitude, longitude, location FROM utilityapp_venue")

venues_list = []
for item in cursor:
	venues_list.append(item)

ok_break = False

venues_list.sort()

lr_start = 87
lr_end = 225

id = 45514
start_index = -1

for start in venues_list:
	start_index += 1
	if start_index >= lr_start:
		end_index = 0
		for end in venues_list:
			end_index += 1
			if (start_index == lr_start and end_index > lr_end) or start_index > lr_start:
				if (start[0] != end[0] or start[3] != end[3]) and start_index < end_index:
					print "Fetching travel time between %s and %s"%(start[0], end[0])
					url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=%s,%s&destinations=%s,%s&mode=walking&key=AIzaSyCfewwBSwN7vzdUm3ejER6Zz4sC2ftiQ7s" %(start[1], start[2], end[1], end[2])
					response = urllib2.urlopen(url)
					jsongeocode = response.read()
					x = json.loads(jsongeocode)
					url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=%s,%s&destinations=%s,%s&mode=driving&key=AIzaSyCfewwBSwN7vzdUm3ejER6Zz4sC2ftiQ7s" %(start[1], start[2], end[1], end[2])
					response = urllib2.urlopen(url)
					jsongeocode = response.read()
					y = json.loads(jsongeocode)
					if x['status'] == "OK" and y['status'] == "OK":
						str = x['rows'][0]['elements'][0]['duration']['text']
						wt = [int(s) for s in str.split() if s.isdigit()]
						if len(wt) == 1:
							walk = wt[0]
						elif len(wt) == 2:
							walk = wt[0]*60 + wt[1]
						else:
							walk = wt[0]*24*60 + wt[1]*60 + wt[2]
						str = y['rows'][0]['elements'][0]['duration']['text']
						dt = [int(s) for s in str.split() if s.isdigit()]
						if len(dt) == 1:
							drive = dt[0]
						elif len(wt) == 2:
							drive = dt[0]*60 + dt[1]
						else:
							drive = dt[0]*24*60 + dt[1]*60 + dt[2]
						query = """INSERT INTO utilityapp_travel_details VALUES (%s, %s, %s, %s, %s, %s, %s)"""
						cursor2.execute(query, (id, start[0], end[0], walk, drive, start[3], end[3]))
						id += 1
						query = """INSERT INTO utilityapp_travel_details VALUES (%s, %s, %s, %s, %s, %s, %s)"""
						cursor2.execute(query, (id, end[0], start[0], walk, drive, end[3], start[3]))
						id += 1
						print "Travel time between %s and %s added! Walking: %d Driving: %d ---------- %s/92112 added."%(start[0], end[0], walk, drive, id)
						print "Last origin added: %s"%start_index
						print "Last destination added: %s"%end_index
						db.commit()
					else:
						print "-----------------------ERROR!---------------------"
						print "Last origin added: %s"%start_index
						print "Last destination added: %s"%end_index
						print x
						print y
						ok_break = True
						break
	if ok_break:
		break


db.commit()
db.close()
