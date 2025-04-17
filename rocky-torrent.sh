#!/bin/bash

URL=https://rocky8x.sytes.net/transmission
transmission-remote "$URL" -a $1 -n rocky:pbdsN5FmuH2Zb%
notify-send "magnet link added to $URL"
