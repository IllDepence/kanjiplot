""" Foo
"""

import csv
import datetime
import sqlite3
import unicodedata
from collections import OrderedDict, defaultdict
import matplotlib.pyplot as plt
import numpy as np


def select_deck(db_cursor):
    """ Print decks and get user input for choice.
    """

    decks = []
    for row in db_cursor.execute('SELECT id, name FROM decks'):
        d_id = row[0]
        d_name = row[1]
        decks.append((d_id, d_name))
    choices = [deck[1] for deck in decks]

    for i in range(len(choices)):
        print(' ['+str(i)+'] '+choices[i])
    inp = int(input('\n'))
    return decks[inp]


def get_deck_stats(db_cursor, deck_id, already_known=[]):
    stats = {}
    kanji_all = []
    num_kanji_total = 0
    num_cards_total = 0

    query_reviews_of_deck = (
        'SELECT id, cid FROM revlog WHERE cid IN ('
        '    SELECT id from cards WHERE did = ?'
        ') ORDER BY revlog.id'
    )

    query_note_fields_of_card = (
        'SELECT id, flds FROM notes WHERE notes.id = ('
        '    SELECT nid FROM cards WHERE cards.id = ?'
        ')'
    )

    # go through all first reviews of a note in given deck
    card_ids_seen = []
    note_ids_seen = []
    for (timestamp, card_id) in db_cursor.execute(
            query_reviews_of_deck,
            (deck_id,)
    ).fetchall():
        # check if it's the first time we see the note
        if card_id in card_ids_seen:
            # can already skip by card and avoid DB lookup
            continue
        note_id, note_fields = db_cursor.execute(
            query_note_fields_of_card,
            (card_id,)
        ).fetchone()
        if note_id in note_ids_seen:
            # not the first review, skip
            continue
        card_ids_seen.append(card_id)
        note_ids_seen.append(note_id)
        # process first review of note
        date = datetime.datetime.fromtimestamp(
            timestamp/1000
        ).strftime("%y%m%d")
        # picks first field of the flds attribute. allows for "notes"
        # ↓ in other fields that won't be counted
        card_front = note_fields.split('\x1f')[0]
        # look for new kanji
        new_kanji = set()
        for char in card_front:
            try:
                if unicodedata.name(char).find('CJK UNIFIED IDEOGRAPH') >= 0:
                    if char not in kanji_all and char not in already_known:
                        new_kanji.add(char)
                        last_kanji_date = date
            except ValueError:
                pass
        # persist stats for the day
        num_kanji_total += len(new_kanji)
        num_cards_total += 1
        kanji_all += list(new_kanji)
        stats[date] = {
            'num_kanji_total': num_kanji_total,
            'num_cards_total': num_cards_total,
            'kanji_all': kanji_all,
            'kanji_new': list(new_kanji)
        }
        last_cards_date = date

    # add stats for today
    today = datetime.datetime.now().strftime("%y%m%d")
    if last_cards_date != today:
        num_kanji_total_last_count = stats[last_kanji_date]['num_kanji_total']
        num_cards_total_last_count = stats[last_cards_date]['num_cards_total']
        stats[today] = {
            'num_kanji_total': num_kanji_total_last_count,
            'num_cards_total': num_cards_total_last_count,
            'kanji_all': kanji_all,
            'kanji_new': ''
        }

    return stats


def kanjiplot_multi():
    """ Plot kanjistats for multiple deck variants
        (recognition+recall, recall only, given name recall only)
    """

    anki_db_fp = 'collection.anki2'
    jouyou_fp = '/home/tarek/data_personal/projects/japanese/res/jouyou_kanji'
    conn = sqlite3.connect(anki_db_fp)
    db_cursor = conn.cursor()

    decks_stats = {
        'recognition+recall': None,
        'recall only': None,
        'given name recall only': None
    }
    already_known = []
    for d_type in decks_stats.keys():
        print(f'Select your {d_type} deck')
        deck_tpl = select_deck(db_cursor)
        deck_id = deck_tpl[0]
        stats = get_deck_stats(db_cursor, deck_id, already_known)
        # remeber kanji from previous deck
        already_known += stats[list(stats.keys())[-1]]['kanji_all']
        decks_stats[d_type] = stats
    return decks_stats

    with open(jouyou_fp) as f:
        jouyou_kanji = list(f.read().strip())

    # determine number of accumulatively covered jouyou kanji
    data_points_tmp = {}
    covered_kanji_str = ''
    for k, vals in data_points_full.items():
        covered_kanji_str += vals[0] + vals[1]
        covered = set(jouyou_kanji).intersection(set(covered_kanji_str))
        vals_ext = vals.copy()
        vals_ext += [len(covered)]
        data_points_tmp[k] = vals_ext
    data_points_full = data_points_tmp

    # persist in TSV file
    with open('kanji_ext.tsv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow([
            'date', 'new_rw', 'new_ro', 'kanji_rw',
            'kanji_ro', 'words_rw', 'words_ro', 'jouyou_covered'
        ])
        for k, v in data_points_full.items():
            writer.writerow([k] + v)

    dates = [
        datetime.datetime.strptime(s, '%y%m%d') for s in data_points_full.keys()
    ]

    rw_kanji = [v[2] for v in data_points_full.values()]
    r_kanji = [
        v[2]+v[3] for v in data_points_full.values() if v[3] > 0
    ]
    covered_jouyou = [v[6] for v in data_points_full.values()]
    dates_r_kanji = dates[-len(r_kanji):]

    rw_words = [v[4] for v in data_points_full.values()]
    r_words = [
        v[4]+v[5] for v in data_points_full.values() if v[5] > 0
        ]
    dates_r_words = dates[-len(r_words):]

    out_dpi = 96
    fig, ax1 = plt.subplots(figsize=(700/out_dpi, 300/out_dpi), dpi=out_dpi)
    ax1.plot(dates, rw_kanji, label='recognition + recall')
    ax1.plot(dates_r_kanji, r_kanji, label='recognition only')
    ax1.plot(dates, covered_jouyou, label='jouyou coverage', alpha=0.5)
    ax1.set_ylim(0)
    ax1.grid()
    plt.yticks(
        np.concatenate(
            (
                np.arange(0, 2000, step=500),
                np.arange(2000, max(r_kanji), step=200)
            )
        )
    )

    fig.legend(loc='center')
    fig.tight_layout()
    fig.savefig('merged.png', dpi=out_dpi)


if __name__ == '__main__':
    kanjiplot_multi()
