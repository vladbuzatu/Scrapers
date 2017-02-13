# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
import urllib2
import unicodedata
import MySQLdb

def encode(x):
	return "0"*(4 - len(str(x))) + str(x)

def get_venue_no(x):
	return x[10:len(x)]

db = MySQLdb.connect("localhost", "root", "admin", "gw_db")
cursor = db.cursor()

venues = []

def replace(x, c, replacement):
	while x.encode('utf8').find(c) != -1:
			poz = x.encode('utf8').find(c)
			x = x[0:poz] + replacement + x[poz+1:len(x)]
	y = x
	return y

for urlindex in range(1,17):

	url = 'https://tickets.edfringe.com/venues?page=' + str(urlindex)
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page.read())
	lst = []
	
	rank = soup.findAll("div", {"class": "col-xs-12 col-md-9 venue-details"})

	for r in rank:
		# get venue name
		venue = r.find("a").contents
		venueName = venue[0]

		while venueName.find("&#039;") != -1:
			poz = venueName.find("&#039;")
			venueName = venueName[0:poz] + "'" + venueName[poz+6:len(venue[0])]

		while venueName.find("&amp;") != -1:
			poz = venueName.find("&amp;")
			venueName = venueName[0:poz] + "&" + venueName[poz+5:len(venue[0])]

		venueName = replace(venueName, "–", "-")
		venueName = replace(venueName, "’", "'")
		venueName = replace(venueName, "ç", "c")
		venueName = replace(venueName, "è", "e")
		venueName = replace(venueName, "é", "e")
		location = venueName

		# get venue address and number
		details = r.findAll("li", {"class": "col-xs-12 list-group-item pull-left"})
		address = details[0].contents[1]
		while address.find("&#039;") != -1:
			poz = address.find("&#039;")
			address = address[0:poz] + "'" + address[poz+6:len(venue[0])]

		while address.find("&amp;") != -1:
			poz = address.find("&amp;")
			address = address[0:poz] + "&" + address[poz+5:len(venue[0])]
		print address
		address = replace(address, "–", "-")
		address = replace(address, "’", "'")
		address = replace(address, "ç", "c")
		address = replace(address, "è", "e")
		address = replace(address, "é", "e")
		address = address.decode('unicode_escape').encode('ascii','ignore')

		venueID = encode(get_venue_no(str(details[1].contents[1])))

		# get accessibility details
		level_access = False
		assistance_dogs = False
		wc_toilets = False
		acc_parking = False

		access = r.findAll("li", {"class": "col-xs-12 list-group-item pull-left hidden-xs"})
		acc = access[0].findAll("span")
		for a in acc:
			if a.contents[0] == "Level Access":
				level_access = True
			elif a.contents[0] == "Assistance Dogs Allowed":
				assistance_dogs = True
			elif a.contents[0] == "Wheelchair Accessible Toilets":
				wc_toilets = True
			elif a.contents[0] == "Accessible Parking":
				acc_parking = True
			if a.contents[0] not in lst:
				lst += [a.contents[0]]

		# get coordinates
		coord = r.findAll("li")
		coo = str(coord[3])[14:]
		index = 0
		lat = ''
		while coo[index] != "\"":
			lat += coo[index]
			index += 1
		latitude = float(lat)

		index += 12
		lng = ''
		while coo[index] != "\"":
			lng += coo[index]
			index += 1
		longitude = float(lng)
		
		# add venue to database
		query = """INSERT INTO utilityapp_venue VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
		if (venueID, address, location) not in venues:
		  	cursor.execute(query, (venueID, location, assistance_dogs, level_access, wc_toilets, acc_parking, address, latitude, longitude))
		venues.append((venueID, address, location))
		print "#####################"
		print "#### VENUE ADDED ####"
		print "Venue ID: %s"%venueID
		print "Location: %s"%location
		print "Address: %s"%address
		print "Coordinates - Latitude: %s, Longitude: %s "%(latitude, longitude)
		print "Assistance Dogs Allowed: %s"%assistance_dogs
		print "Level Access: %s"%level_access
		print "Wheelchair Accessible Toilets: %s"%wc_toilets
		print "Accessible Parking: %s"%acc_parking
		
db.commit()
db.close()