#!/bin/bash
# TRANSMISSION_BT_AUT and TRANSMISSION_BT_URL must be set as env var
r=$(transmission-remote "$TRANSMISSION_BT_URL" -a $1 -n $TRANSMISSION_BT_AUT | grep -o "responded: .*" | cut -d " " -f2)
# notify-send -ea "R.Torrent" -t 3000 "Torrent added" "$r"
dunstify -a "R.Torrent" -t 3000 "Torrent added: $r" "$TRANSMISSION_BT_URL"