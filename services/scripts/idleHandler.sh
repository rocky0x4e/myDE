#!/bin/bash

IDLE_DURATION=1800 # second
DELAY=60

# currentH=$(date +%H)
# if [[ $currentH -gt 4 && $currentH -lt 21 ]]; then exit; fi

idle=$(xprintidle)
idle=$((idle / 1000))
if [[ $idle -gt $IDLE_DURATION ]]; then
    dID=$(notify-send -pet $(( DELAY * 1000 )) -u critical "System!!!" "System suspend in a ${DELAY} seconds")
    curl -d "System suspend in ${DELAY} seconds" https://ntfy.sh/MSI-laptop-alerts

    paplay ~/Music/sound/ding-36029.mp3 >/dev/null 2>&1 &
    sleep $DELAY
    if [[ ! -z $dID ]]; then notify-send -r $dID; fi
    idle2=$(xprintidle)
    idle2=$((idle2 / 1000))
    if [[ $idle2 -gt $IDLE_DURATION ]]; then
        idleMinute=$(( idle2 / 60 ))
        echo "Idled for $idle seconds (~ $idleMinute minutes)!!!"
        systemctl suspend
    fi
fi
