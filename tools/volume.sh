#!/bin/bash

MAX_VOL=120

arg="$1"
sink=$(pactl get-default-sink)
outputDevName=$(pactl -f json list sinks | jq -r '
  .[] | select(.name == "'"$sink"'") | .description
')

function flash {
    t=/tmp/volume.sh.tmp
    l=${t}.lock
    icon=$HOME/.local/share/icons/rofi/512x512/apps/audio-waves.png
    exec 200>"$l" || return 1
    flock -n 200 || {
        echo "Another instance is running. skip notification."
        return 1
    }
    rid=$(cat $t 2> /dev/null) || reutrn 0
    if [[ ! -z $rid ]]; then replace="-r $rid" ;fi
    stt=$(pactl get-sink-mute "$sink" | cut -d " " -f2)
    if [[ "$stt" == "yes" ]]; then icon="$HOME/.local/share/icons/rofi/512x512/apps/audio-volume-muted.png"; fi

    nid=$(dunstify -t 2000 -p $replace -a "" "${vol}%" "${outputDevName}" \
        --hints=int:value:$vol \
        --hints=string:image-path:$icon )
    echo $nid > $t
}

function getVol {
    echo -n $(pactl get-sink-volume "$sink" | awk -F '/' '{print $2}' | head -n1 | tr -d ' %')
}

case "$arg" in
    [0-9]*)
        if [[ $arg -gt $MAX_VOL ]]; then vol=$MAX_VOL; else vol=$arg; fi
        pactl set-sink-volume "$sink" "$vol%"
        ;;
    [-+][0-9]*)
        vol=$(getVol)
        vol=$(($vol / $arg * $arg $arg))
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