# -*- coding: utf-8 -*-

import sqlite3
import unicodedata
import datetime

conn = sqlite3.connect('collection.anki2')
c = conn.cursor()
notes = 0
kanji = []
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
					notes = notes + 1
		except ValueError:
			pass

print(notes)
