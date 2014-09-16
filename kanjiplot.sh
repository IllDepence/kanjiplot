#!/bin/bash

if [ $# -eq 0 ]
then
    python3 kanjiplot.py
else
    python3 kanjiplot.py $1
    if [ $1 == "find" ]
    then
        exit
    fi
fi

gnuplot kanjiplot.p
mv kanji.dat web
