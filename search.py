from bs4 import BeautifulSoup
from urllib import *
import time
from datetime import datetime
import csv
import os.path
import smtplib
from email.mime.text import MIMEText
import sys


def find_results(location, query):
	home_url = "http://" + location + ".craigslist.org"

	search = "/search/sss?sort=rel"

	parameters = {}

	parameters["&query="] = query

	search_url = home_url + search
	for k in parameters:
		search_url += k + parameters[k]

	soup = BeautifulSoup(urlopen(search_url).read())
	items = soup.find_all("p", "row")
	results = []
	for item in items:
		try:
			a_tag = item.find_all('a')[1]
			product = a_tag.contents[0]
			item_link = a_tag.get('href')
			if item_link[0] == '/':
				item_link = home_url + item_link
			price = int(item.find('span', 'price').contents[0].lstrip('$'))
			time_string = item.find('time').get('datetime')
			timestruct = time.strptime(time_string, "%Y-%m-%d %H:%M")
			dt = datetime.fromtimestamp(time.mktime(timestruct))
			results.append([item_link, product, price, dt])
		except:
			print "***ERROR SOMEWHERE***", item_link
			continue
	return results

def find_new(location, query, results):
	filename = location + "_" + query + ".csv"
	if os.path.isfile(filename):
		with open(filename, 'rb') as csvValues:
			visited_products = [row[0] for row in csv.reader(csvValues)]
	else:
		open(filename, 'wb')
		visited_products = []
	new_products = [item for item in results if item[0] not in visited_products]
	return new_products

def update(location, query, new_products):
	filename = location + "_" + query + ".csv"
	with open(filename, 'a') as csvValues:
		add = csv.writer(csvValues)
		for new_product in new_products:
			add.writerow(new_product)

def reset(location, query):
	os.remove(location + "_" + query + ".csv")

def reset(filename):
	os.remove(filename)

def email(location, item, new_products, toaddr):
	content = str(len(new_products)) + " new products\n\n"
	for np in new_products:
		item_link, product, price, dt = np
		content += item_link + "\n"
		content += product + "\n"
		content += "$" + str(price) + "\n"
		content += str(dt) + "\n\n"
	msg = MIMEText(content)

	fromaddr = "larrybearrr@gmail.com"
	username = 'larrybearrr'
	password = 'pw12345678'

	msg['Subject'] = item + " from " + location + ": Update at UTC " + str(datetime.utcnow())
	msg['From'] = fromaddr
	msg['To'] = toaddr

	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(username,password)
	server.sendmail(fromaddr, toaddr, msg.as_string())
	server.quit()

if __name__ == "__main__":
	email_boo = True
	location = "sfbay"
	item = "arduino"
	toaddr = "alanchen1st@gmail.com"

	loc_in = raw_input("location? ")
	if loc_in != "skip" and loc_in != "default":
		location = loc_in
		item = raw_input("item? ")
		toaddr = raw_input("email? ")

	query = item.replace(" ", "+")
	results = find_results(location, query)
	new_products = find_new(location, query, results)
	if new_products:
		update(location, query, new_products)
		if email_boo:
			email(location, item, new_products, toaddr)
			print "emailed to " + toaddr
	else:
		print "no new products"
