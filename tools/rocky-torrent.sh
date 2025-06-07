#!/bin/bash

URL=https://rocky-0x4e.sytes.net/transmission
r=$(transmission-remote "$URL" -a $1 -n rocky:pbdsN5FmuH2Zb% | grep -o "responded: .*" | cut -d " " -f2)
# notify-send -ea "R.Torrent" -t 3000 "Torrent added" "$r"
dunstify -a "R.Torrent" -t 3000 "Torrent added: $r" "$URL"