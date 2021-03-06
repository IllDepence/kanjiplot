unset log
unset label
set xdata time
set timefmt "%y%m%d"
set format x "%b %y"
set xrange ["130515":]
set xtics rotate
set xtics 5256000 font "Dejavu Sans, 10"
set y2tics font "Dejavu Sans, 10"
set ytics format ""
set grid
set key left top
set terminal png size 700, 300
set output "output.png"
plot "kanji.dat" using 1:3 with linespoints lc rgb '#e04646' lt 1 lw 2 pt 0 ps 0 title "vocab", "kanji.dat" using 1:2 with linespoints lc rgb '#0060ad' lt 1 lw 2 pt 0 ps 0 title "kanji"
