#!/bin/bash

MAX_VOL=120
ICON_UNMUTED="$HOME/.local/share/icons/wmicons/512x512/apps/audio-waves.png"
ICON___MUTED="$HOME/.local/share/icons/wmicons/512x512/apps/audio-volume-muted.png"

t=/tmp/volume.sh.tmp
sink=$(pactl get-default-sink)
allSinks=$(pactl -f json list sinks)
output=$(echo "$allSinks" | jq -r --arg s "$sink" '.[] | select(.name == $s) | (.properties."device.profile.description" // .description)')
isMuted=$(echo "$allSinks" | jq -r --arg s "$sink" '.[] | select(.name == $s) | .mute')

function flash {
    l=${t}.lock
    icon=$ICON_UNMUTED
    exec 200>"$l" || return 1
    flock -n 200 || {
        echo "Another instance is running. skip notification."
        return 1
    }
    rid=$(cat $t 2> /dev/null) || reutrn 0
    if [[ ! -z $rid ]]; then replace="-r $rid" ;fi
    if [[ "$isMuted" == "true" ]]; then icon=$ICON___MUTED; fi

    nid=$(notify-send -t 2000 -p $replace -a "" "${vol}%" "${output}" \
        --hint=int:value:$vol \
        --hint=string:image-path:$icon )
    echo $nid > $t
}

function getVol {
    echo -n $(pactl get-sink-volume "$sink" | awk -F '/' '{print $2}' | head -n1 | tr -d ' %')
}

case "$1" in
    [0-9]*)
        if [[ $1 -gt $MAX_VOL ]]; then vol=$MAX_VOL; else vol=$1; fi
        pactl set-sink-volume "$sink" "$vol%"
        ;;
    [-+][0-9]*)
        vol=$(getVol)
        vol=$(($vol / $1 * $1 $1))
        if [[ $vol -gt $MAX_VOL ]]; then vol=$MAX_VOL;
        elif [[ $vol -lt 0 ]]; then vol=0; fi
        pactl set-sink-volume "$sink" "$vol%"
        ;;
    toggle)
        vol=$(getVol)
        pactl set-sink-mute "$sink" toggle
        ;;
    get)
        echo -n $(getVol)
        exit 1
        ;;
    *)
        echo "Usage: $0 +N|-N|N|toggle|get (N: percentage)"
        exit 1
        ;;
esac
flash