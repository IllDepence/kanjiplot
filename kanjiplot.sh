#!/bin/sh

table_id=1367422637589

python kanjiplot.py $table_id
gnuplot kanjistats.p
rm kanji.dat
