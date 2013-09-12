unset log
unset label
set xdata time
set timefmt "%y%m%d"
set format x "%d %b"
#set xrange ["130515":]
set xtics 2592000 font "Dejavu Sans, 10"
set ytics 50 font "Dejavu Sans, 10"
set grid
set terminal png size 700, 300
set output "output.png"
plot "kanji.dat" using 1:2 with linespoints notitle lc rgb '#0060ad' lt 1 lw 1 pt 1 ps 1.5
