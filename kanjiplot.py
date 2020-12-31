# -*- coding: utf-8 -*-

import datetime
import json
import sqlite3
import sys
import unicodedata


def select_deck(db_cursor):
    decks = []
    for row in db_cursor.execute('SELECT id, name FROM decks'):
        d_id = row[0]
        d_name = row[1]
        decks.append((d_id, d_name))
    choices = [deck[1] for deck in decks]

    print('Which deck would you like to plot?\n')

    for i in range(len(choices)):
        print(' ['+str(i)+'] '+choices[i])
    inp = int(input('\n'))
    return decks[inp]

conn = sqlite3.connect('collection.anki2')
db_cursor = conn.cursor()
raw_abs = False

if(sys.platform == 'win32'):
    kanjiplot_command = 'kanjiplot '
    write_flags = 'wb'
else:
    kanjiplot_command = './kanjiplot.sh '
    write_flags = 'w'

if(len(sys.argv) < 2 or sys.argv[1] == 'raw_abs'):
    if len(sys.argv) == 2:
        if(sys.argv[1] == 'raw_abs'):
            raw_abs = True
    deck_tpl = select_deck(db_cursor)
    deck_id = deck_tpl[0]
else:
    if(sys.argv[1] == 'find'):
        deck_tpl = select_deck(db_cursor)
        print(('\ndeck "{}" has ID {}\n\nrun the following command for automat'
               'ed plotting:\n{}{}\n\n\n').format(deck_tpl[1],
                                                  deck_tpl[0],
                                                  kanjiplot_command,
                                                  deck_tpl[0]))
        sys.exit(0)
    deck_id = sys.argv[1]

dates = []
kanji = []
data_points = dict()
total = 0

cards_data_points = dict()
cards_total = 0

kanji_data_points = dict()

for row in db_cursor.execute(
        'SELECT id, flds FROM notes WHERE id IN (SELECT nid FROM'
        ' cards WHERE did = ?) ORDER BY id', (deck_id,)):
    timestamp = row[0]
    date = datetime.datetime.fromtimestamp(timestamp/1000).strftime("%y%m%d")
    data_pre = row[1]
    data = data_pre.split(u'\x1f')[0]
    # ↑ picks first field of the flds attribute. allows for "notes" in other
    # fields that won't be counted

    cards_total += 1
    cards_data_points[date] = cards_total
    last_cards_date = date
    if date not in kanji_data_points:
        kanji_data_points[date] = ''
    for i in range(0, len(data)):
        char = data[i]
        try:
            if unicodedata.name(char).find('CJK UNIFIED IDEOGRAPH') >= 0:
                if char not in kanji:
                    total += 1
                    kanji.append(char)
                    if date not in dates:
                        dates.append(date)
                        last_kanji_date = date
                    data_points[date] = total
                    if raw_abs:
                        kanji_data_points[date] = ''
                        for i in range(0, len(kanji)):
                            kanji_data_points[date] += kanji[i]
                    else:
                        if kanji_data_points[date].find(char) == -1:
                            kanji_data_points[date] += char
        except ValueError:
            pass
    if date not in dates:
        dates.append(date)
        last_kanji_date = date
    data_points[date] = total

today = datetime.datetime.now().strftime("%y%m%d")
added_today = False
if not raw_abs and not dates[-1] == today:
    dates.append(today)
    data_points[today] = data_points[last_kanji_date]
    cards_data_points[today] = cards_data_points[last_cards_date]
    added_today = True

f = open('kanji.dat', write_flags)
fr = open('timelapse/kanji_raw.dat', write_flags)
for d in dates:
    f.write('{} {} {}\n'.format(d, data_points[d], cards_data_points[d]))
    if added_today and d == today:
        continue
    if sys.platform == 'win32':
        fr.write(str(d) + ' ' + kanji_data_points[d].encode('utf8') + '\n')
    else:
        fr.write(str(d) + ' ' + str(kanji_data_points[d]) + '\n')
