# -*- coding: utf-8 -*-

import datetime
import json
import sqlite3
import sys
import unicodedata

def select_deck():
    decks = []
    for row in c.execute('SELECT decks FROM col'):
        deks = json.loads(row[0])
        for key in deks:
            d_id = deks[key]['id']
            d_name = deks[key]['name']
            decks.append((d_id, d_name))

    print('Which deck would you like to plot?\n')

    for i in range(len(decks)):
        print(' ['+str(i)+'] '+decks[i][1])
    inp = int(input('\n'))
    return decks[inp]

conn = sqlite3.connect('collection.anki2')
c = conn.cursor()
with_raw = False
raw_rel = False

if(len(sys.argv) < 2 or sys.argv[1] == 'with_raw_abs' or sys.argv[1] == 'with_raw_rel'):
    if(sys.argv[1] == 'with_raw_abs'):
        with_raw = True
    if(sys.argv[1] == 'with_raw_rel'):
        with_raw = True
        raw_rel = True
    deck_tpl = select_deck()
    deck_id = deck_tpl[0]
else:
    if(sys.argv[1] == 'find'):
        deck_tpl = select_deck()
        print('\ndeck "'+deck_tpl[1]+'" has ID '+str(deck_tpl[0])+'\n\nrun the following command for automated plotting:\n./kanjiplot.sh '+str(deck_tpl[0])+'\n\n\n')
        sys.exit(0)
    deck_id = sys.argv[1]

dates = []
kanji = []
data_points = dict()
total = 0

cards_data_points = dict()
cards_total = 0

kanji_data_points = dict()

for row in c.execute('SELECT id, flds FROM notes WHERE id IN (SELECT nid FROM cards WHERE did IS ' + str(deck_id) + ') ORDER BY id'):
    timestamp = row[0]
    date = datetime.datetime.fromtimestamp(timestamp/1000).strftime("%y%m%d")
    data = row[1]
    cards_total += 1
    cards_data_points[date] = cards_total
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
                    if with_raw:
                        if not date in kanji_data_points:
                            kanji_data_points[date] = ''
                        if not raw_rel:
                            kanji_data_points[date] = ''
                        if raw_rel:
                            if(kanji_data_points[date].find(char) == -1):
                                kanji_data_points[date] += char
                        else:
                            for i in range(0, len(kanji)):
                                kanji_data_points[date] += kanji[i]
        except ValueError:
            pass

f = open('kanji.dat', 'w')
if with_raw:
    fr = open('kanji_raw.dat', 'w')
for d in dates:
    if with_raw:
        fr.write(str(d) + ' ' + str(kanji_data_points[d]) + '\n')
    f.write(str(d) + ' ' + str(data_points[d]) + ' ' + str(cards_data_points[d]) + '\n')
