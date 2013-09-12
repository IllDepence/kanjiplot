# -*- coding: utf-8 -*-

import sqlite3
import unicodedata
import datetime

def addUp():
	sum = 0
	for d in data_points:
		sum = sum + data_points[d]
	return sum

conn = sqlite3.connect('collection.anki2')
c = conn.cursor()
dates = []
kanji = []
data_points = dict()
for row in c.execute('SELECT id, flds FROM notes WHERE mid IS 1367422637589 ORDER BY id'):
	timestamp = row[0]
	date = datetime.datetime.fromtimestamp(timestamp/1000).strftime("%y%m%d")
	data = row[1]
	for i in range(0, len(data)):
		char = data[i]
		try:
			if(unicodedata.name(char).find('CJK UNIFIED IDEOGRAPH') >= 0):
				if(not char in kanji):
					kanji.append(char)
					if(not date in dates):
						print(addUp())
						dates.append(date)
						data_points[date] = 0
					data_points[date] += 1
		except ValueError:
			pass
for d in data_points:
	#print(str(d) + ' ' + str(data_points[d]))
	pass
