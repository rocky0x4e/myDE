#!/bin/bash

MAX_VOL=120

arg="$1"
sink=$(pactl get-default-sink)
outputDevName=$(pactl -f json list sinks | jq -r '
  .[] | select(.name == "'"$sink"'") | .description
')
vol=$(pactl get-sink-volume "$sink" | awk -F '/' '{print $2}' | head -n1 | tr -d ' %')
vol=$(($vol / $arg * $arg $arg))
if [[ $vol -gt $MAX_VOL ]]; then vol=$MAX_VOL; fi

function flash {
    t=/tmp/volume.sh.tmp
    l=${t}.lock
    icon=file:/$HOME/.local/share/icons/rofi/512x512/apps/audio-waves.png
    exec 200>"$l" || return 1
    flock -n 200 || {
        echo "Another instance is running. skip notification."
        return 1
    }
    rid=$(cat $t 2> /dev/null) || reutrn 0
    if [[ ! -z $rid ]]; then replace="-r $rid" ;fi
    if [[ "$2" == "yes" ]]; then icon="file:/$HOME/.local/share/icons/rofi/512x512/apps/audio-volume-muted.png"; fi
    nid=$(notify-send -t 2000 -ep $replace -a "" "${outputDevName}" "${1}%" \
            --hint=int:value:$1 \
            --hint=string:image-path:$icon )
    echo $nid > $t
}

case "$arg" in
    +[0-9]*)
        pactl set-sink-volume "$sink" "$vol%"
        ;;
    -[0-9]*)
        pactl set-sink-volume "$sink" "$vol%"
        ;;
    toggle)
        pactl set-sink-mute "$sink" toggle
        ;;
    *)
        echo "Usage: $0 [+N|-N|toggle]"
        exit 1
        ;;
esac
stt=$(pactl get-sink-mute "$sink" | cut -d " " -f2)
flash $vol $stt

