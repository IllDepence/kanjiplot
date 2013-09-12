# -*- coding: utf-8 -*-

import sqlite3
import unicodedata
import datetime

conn = sqlite3.connect('collection.anki2')
c = conn.cursor()
dates = []
kanji = []
data_points = dict()
total = 0
for row in c.execute('SELECT id, flds FROM notes WHERE mid IS 1367422637589 ORDER BY id'):
	timestamp = row[0]
	date = datetime.datetime.fromtimestamp(timestamp/1000).strftime("%y%m%d")
	data = row[1]
	for i in range(0, len(data)):
		char = data[i]
		try:
			if(unicodedata.name(char).find('CJK UNIFIED IDEOGRAPH') >= 0):
				if(not char in kanji):
					total += 1
					kanji.append(char)
					if(not date in dates):
						dates.append(date)
					data_points[date] = total
		except ValueError:
			pass

f = open('kanji.dat', 'w')
for d in dates:
	f.write(str(d) + ' ' + str(data_points[d]) + '\n')
