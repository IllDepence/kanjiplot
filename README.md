![](http://moc.sirtetris.com/kanjiplot0.gif "kanjiplot")
![](http://moc.sirtetris.com/kanjiplot1.gif "kanjiplot")

###USAGE
- copy Anki's `collection.anki2` file into kanjiplot folder
- run `./kanjiplot.sh`
- a dialog will appear, choose your kanji deck
- view `output.png`


###SCRIPTING
- run `./kanjiplot.sh find`
- a dialog will appear, choose a deck
- the `<deck_id>` will be printed
- run `./kanjiplot.sh <deck_id>` for automated plotting


###WEB
- put contents of folder `web` on a webserver
- enjoy a d3.js powered interactive graph


###TIMELAPSE
- view `timelapse/index.html` in your browser of choice (chromium requires flag `--allow-file-access-from-files`)
- to view absolute states (meant for "Show specific day") run `./kanjiplot.sh raw_abs`


###NOTE
The script determines the number of kanji in your deck for every day you added at least one card, hence it will only work for self created decks where cards are added over time.


###WINDOWS USERS
- Use `kanjiplot.bat` instead of `kanjiplot.sh`
- Python and gnuplot must be installed and available in the PATH before you run `kanjiplot.bat`
- You may have to edit the file `kanjiplot.p` to use another font if you don't have Dejavu Sans installed (Tahoma should work fine)
