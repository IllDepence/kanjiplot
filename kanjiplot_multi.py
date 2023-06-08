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
    last_kanji_date = None
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
        num_new_kanji_review = 0
        if date != last_kanji_date:
            # reset if review is on a new day
            new_kanji = set()
        else:
            # continue adding if review is on the same day than previous
            new_kanji = set(stats[last_kanji_date]['kanji_new'])
        for char in card_front:
            try:
                if unicodedata.name(char).find('CJK UNIFIED IDEOGRAPH') >= 0:
                    if char not in kanji_all and char not in already_known:
                        new_kanji.add(char)
                        num_new_kanji_review += 1
                        last_kanji_date = date
            except ValueError:
                pass
        # persist stats for the day
        num_kanji_total += num_new_kanji_review
        num_cards_total += 1
        kanji_all += list(new_kanji)
        stats[date] = {
            'num_kanji_total': num_kanji_total,
            'num_cards_total': num_cards_total,
            'kanji_all': kanji_all.copy(),
            'kanji_new': list(new_kanji.copy())
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

    # set up DB
    anki_db_fp = 'collection.anki2'
    conn = sqlite3.connect(anki_db_fp)
    db_cursor = conn.cursor()

    # get deck stats
    decks_stats = {
        'recognition+recall': None,
        'recall only': None,
        'given name recall only': None
    }
    in_previous_decks = []
    for d_type in decks_stats.keys():
        print(f'Select your {d_type} deck')
        deck_tpl = select_deck(db_cursor)
        deck_id = deck_tpl[0]
        stats = get_deck_stats(db_cursor, deck_id, in_previous_decks)
        # remeber kanji from previous deck
        in_previous_decks += stats[list(stats.keys())[-1]]['kanji_all']
        decks_stats[d_type] = stats


    # determine accumulative stats for
    # - jouyou coverage
    # - reco_reca
    # - reco+reca and reca only
    # - reco+reca and reca only and reca in given names only (all)
    jouyou_fp = '/home/tarek/data_personal/projects/japanese/res/jouyou_kanji'
    with open(jouyou_fp) as f:
        jouyou_kanji = set(f.read().strip())
    # # get list of all dates for which data points exist across decks
    joint_dates = []
    for stats in decks_stats.values():
        joint_dates.extend(stats.keys())
    joint_dates = list(set(joint_dates))
    joint_dates.sort()
    jouyou_coverage = []
    num_kanji_rw = []
    num_kanji_rwro = []
    num_kanji_rwroro_names = []
    num_words_total = []
    covered_kanji = set()
    nrw, nrwro, nrwroron, nword = (0, 0, 0, 0)
    for i, date in enumerate(joint_dates):
        # get new kanji from all deck types
        kanji_new_rw = decks_stats['recognition+recall'].get(
            date, defaultdict(list)
        )['kanji_new']
        kanji_new_ro = decks_stats['recall only'].get(
            date, defaultdict(list)
        )['kanji_new']
        kanji_new_gnro = decks_stats['given name recall only'].get(
            date, defaultdict(list)
        )['kanji_new']
        # # get words counts from vocab deck types
        # nwords_

        # update stats
        covered_kanji.update(
            kanji_new_rw + kanji_new_ro + kanji_new_gnro
        )
        nrw += len(kanji_new_rw)
        nrwro += len(kanji_new_rw + kanji_new_ro)
        nrwroron += len(kanji_new_rw + kanji_new_ro + kanji_new_gnro)

        # add numbers to lists
        covered_jouyou_kanji = jouyou_kanji.intersection(covered_kanji)
        jouyou_coverage.append(len(covered_jouyou_kanji))
        num_kanji_rw.append(nrw)
        num_kanji_rwro.append(nrwro)
        num_kanji_rwroro_names.append(nrwroron)
        # num_words_total.append(nword)

    plot_dates = list(map(
        datetime.datetime.strptime,
        joint_dates,
        len(joint_dates)*['%y%m%d'])
    )

    for width, height, font_size, fn in [
        (700, 300, 12, 'merged.png'),
        (2100, 900, 20, 'merged_large.png')
    ]:
        out_dpi = 96
        fig, ax1 = plt.subplots(
            figsize=(width/out_dpi, height/out_dpi),
            dpi=out_dpi
        )
        ax1.plot(
            plot_dates,
            jouyou_coverage,
            label='jouyou coverage',
            alpha=0.5
        )
        ax1.plot(
            plot_dates,
            num_kanji_rwroro_names,
            label='recognition only (including proper nouns)'
        )
        ax1.plot(plot_dates, num_kanji_rwro, label='recognition only')
        ax1.plot(plot_dates, num_kanji_rw, label='recognition + recall')
        ax1.set_ylim(0)
        ax1.set_xlim(plot_dates[0], plot_dates[-1])
        ax1.grid()
        plt.yticks(
            np.concatenate(
                (
                    np.arange(0, 2000, step=500),
                    np.arange(2000, max(num_kanji_rwroro_names), step=200)
                )
            )
        )

        plt.legend(
            loc='lower right',
            fontsize=font_size
        )
        plt.tight_layout()
        plt.savefig(fn, dpi=out_dpi)


if __name__ == '__main__':
    kanjiplot_multi()
