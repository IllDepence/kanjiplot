#!/bin/sh

deck_id=1367422637589 # your kanji deck

python kanjiplot.py $deck_id
gnuplot kanjiplot.p
rm kanji.dat
