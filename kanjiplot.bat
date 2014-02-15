@echo off
set argC=0
for %%x in (%*) do Set /A argC+=1
if %argC% EQU 0 (
    python kanjiplot.py 
) else (
    python kanjiplot.py %1
    if "%1" == "find" (
        exit /B
    )
)

gnuplot kanjiplot.p
del kanji.dat
