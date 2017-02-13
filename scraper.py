# -*- coding: utf-8 -*-

# get data from csv, process it and import to MySQL database - 
import csv
import MySQLdb
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def encode(x):
	return "0"*(4 - len(str(x))) + str(x)

def format_age(x):
	if x[0] == "U":
		return 0
	elif x[0:2] == "PG":
		return 8
	elif x[0:2] == "12":
		return 12
	elif x[0:2] == "14":
		return 14
	elif x[0:2] == "16":
		return 16
	return 18

def format_time(x):
	if x.find("hour") != -1:
		minutes = int(x[0:2]) * 60
		if x.find("minute") != -1:
			if x[6] == " ":
				minutes += int(x[7:9])
			elif x[7] == " ":
				minutes += int(x[8:10])
			else:
				minutes += int(x[9:11])
	else:
		minutes = int(x[0:2])

	return minutes

def get_venue_no(x):
	start_index = x.rfind("(Venue ") + 7
	end_index = x.rfind(")")
	string = x[start_index:end_index]
	return encode(int(string))

def get_start_times(x):
	times_list = []
	start_index = 0
	end_index = 5
	while end_index <= len(x) + 1:
		string = x[start_index:start_index+2] + x[end_index-2:end_index]
		times_list += [string]
		start_index += 7
		end_index += 7

	return times_list

def get_dates(x):
	return [y.strip() for y in x[4:len(x)].split(',')]

def format_days(x):
	if x.find("-") == -1:
		if len(x) == 2:
			return x
		else:
			return "0" + x
	else:
		if len(x) == 3:
			return "0" + x[0:2] + "0" + x[2]
		elif len(x) == 4:
			return "0" + x
		else:
			return x

def replace(x, c, replacement):
	while x.encode('utf8').find(c) != -1:
			poz = x.encode('utf8').find(c)
			x = x[0:poz] + replacement + x[poz+1:len(x)]
	y = x
	return y

db = MySQLdb.connect("localhost", "root", "admin", "gw_db")
cursor = db.cursor()
cursor2 = db.cursor()
cursor2.execute("SELECT location FROM utilityapp_venue")

with open('all_data.csv') as csvfile:
	data = csv.reader(csvfile)
	id = 1
	index = 0
	for d in data:
		start_times = get_start_times(d[7])
		dates = get_dates(d[13])
		if index > 0 and d[2].find("CANCELLED") == -1 and len(start_times) != 0 and dates[0] != '':
			eventID = encode(index)
			showName = d[2].decode('unicode_escape').encode('ascii','ignore')
			genre = d[4].decode('unicode_escape').encode('ascii','ignore')
			description = (d[11] + d[12]).decode('unicode_escape').encode('ascii','ignore')
			age_s = format_age(d[9])
			duration = format_time(d[8])
			imageURL = d[0]
			query = """INSERT INTO utilityapp_event VALUES (%s, %s, %s, %s, %s, %s, %s)"""
			cursor.execute(query, (eventID, showName, genre, description, age_s, duration, imageURL))
			print "Show: %s added!!!"%showName
			max_similarity = 0
			venueName = d[6][:d[6].find(" (Venue ")].decode('unicode_escape').encode('ascii','ignore')
			for c in cursor2:
				if (similar(venueName, c[0]) > max_similarity):
					location = c[0]
					max_similarity = similar(venueName, c[0])

			print venueName, location, max_similarity

			for st in start_times:
				for dts in dates:
					date = str(st) + "AUG" + format_days(str(dts))
					if len(date) >= 9:
						query = """INSERT INTO utilityapp_event_date_venue VALUES (%s, %s, %s, %s, %s)"""
						cursor.execute(query, (id, eventID, date, get_venue_no(d[6]), location))
						id += 1
					print "Show time: %s , Show venue: %s"%(date, get_venue_no(d[6]))
		index += 1

db.commit()
db.close()
