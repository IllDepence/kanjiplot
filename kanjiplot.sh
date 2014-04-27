#!/bin/sh

if [ $# -eq 0 ]
then
    python kanjiplot.py
else
    python kanjiplot.py $1
    if [ $1 == "find" ]
    then
        exit
    fi
fi

gnuplot kanjiplot.p
mv kanji.dat web
