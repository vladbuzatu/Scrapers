# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup
import urllib2
import unicodedata
import MySQLdb
import re

db = MySQLdb.connect("localhost", "root", "admin", "gw_db")
cursor = db.cursor()

# url = 'https://www.tripadvisor.com/Restaurants-g186525-Edinburgh_Scotland.html#EATERY_OVERVIEW_BOX'

for pagenumber in range(8,60):

	number = (pagenumber - 1) * 30
	url = 'https://www.tripadvisor.co.uk/Restaurants-g186525-oa' + str(number) + '-Edinburgh_Scotland.html'
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page.read())

	#print str(soup).find("page")
	# x = [m.start() for m in re.finditer("next", str(soup))]

	# for ind in x:
	# 	print "#################"
	# 	print str(soup)[ind:ind+75]
	# 	print "#################"

	x = str(soup)
	y = [m.start() for m in re.finditer("https://media-cdn.tripadvisor.com", x)]

	y = y[5:35]
	imageURLlist = []
	for poz in y:
		imageURLlist.append(x[poz:poz+100][0:x[poz:poz+100].find("\"")])
	index = 0
	indeximg = 0
	for s in soup.findAll("span",{"dir":"ltr"})[1:]:
		if index%2 == 0:
			urlPart = str(s)[str(s).find("et('/") + 5:]
			urlPart = urlPart[:urlPart.find('\'')]
			resURL = "https://www.tripadvisor.com/" + urlPart
			
			page2 = urllib2.urlopen(resURL)
			soup2 = BeautifulSoup(page2.read())

			name = soup2.findAll("h1", {"class": "heading_name  "})[0].contents[2][1:]
			name = name[:len(name)-1]	
			print "Restaurant name: " , name
			phoneNumber = soup2.findAll("div", {"class": "fl phoneNumber"})
			if len(phoneNumber) != 0:
				phoneNumber = phoneNumber[0].contents[0]
			else:
				phoneNumber = ""
			print "Phone number: " , phoneNumber
			r = str(soup2.findAll("span", {"class": "rate sprite-rating_rr rating_rr"}))
			rating = r[r.find("content=") + 9:r.find("content=") + 12]
			print "Rating: " , rating

			ft = soup2.findAll("a",{"onclick":"ta.setEvtCookie('RESTAURANT_DETAILS', 'RESTAURANTS_DETAILS_CUISINE', '', 0, this.href);"})



			lst = []
			for f in ft:
				lst.append(f.contents[0])

			print "Food type: " , lst
			foodType = lst

			streetName = soup2.findAll("span",{"class":"street-address"})[0].contents
			if len(streetName) != 0:
				streetName = streetName[0]
			else:
				streetName = ""
			print "Street: ", streetName 

			postcode = soup2.findAll("span",{"property":"postalCode"})[0].contents[0]
			print postcode.find("EH")
			ok = True

			if postcode.find("EH") == 0:
				ok = True
			else:
				postcode = "NOT DEFINED!!"
			print "Postcode: " , postcode

			imageURL = imageURLlist[indeximg]
			indeximg += 1
			print "Image URL: ", imageURL

			query = """INSERT INTO utilityapp_restaurant VALUES (%s, %s, %s, %s, %s, %s, %s)"""
			cursor.execute(query,(name, streetName, postcode, phoneNumber, rating, str(foodType), imageURL))
			db.commit()
		index += 1
		# for s in soup2.findAll("img"):
		# 	print s
		# 	print



