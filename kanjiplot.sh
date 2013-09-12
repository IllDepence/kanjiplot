#!/bin/sh

table_id=1367422637589

python kanjiplot.py $table_id
gnuplot kanjiplot.p
rm kanji.dat
