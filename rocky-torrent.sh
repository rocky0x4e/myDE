#!/bin/bash

URL=https://rocky-0x4e.sytes.net/transmission
r=$(transmission-remote "$URL" -a $1 -n rocky:pbdsN5FmuH2Zb%)
notify-send -ea "Torrent" "Torrent added" "$r"
