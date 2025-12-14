#!/bin/bash
NPID=0
isMuted(){
    m=yes
    inputSOURCES=($(pactl list short sources | grep input | cut -f1))

    for source in "${inputSOURCES[@]}"; do
        r=$(pactl get-source-mute $source | cut -d " " -f2)
        if [[ $r == "no" ]]; then
            m=no
            break
        fi
    done
    echo $m
}

status() {
    if [ "$(isMuted)" = "yes" ]; then
        pbIcon=""
        nIcon="microphone-sensitivity-muted-symbolic"
        txtStatus=Muted
    else
        pbIcon=""
        nIcon="microphone-sensitivity-high-symbolic"
        txtStatus=Unmuted
        inputSOURCES=($(pactl list short sources | grep input | cut -f1))
        for source in "${inputSOURCES[@]}"; do 
            pactl set-source-mute "$source" 0
        done
    fi

    echo $pbIcon
    activeWindowId=$(xprop -root _NET_ACTIVE_WINDOW | cut -d " " -f 5)
    if [[ -z $activeWindowId ]]; then return; fi
    if [[ $activeWindowId != "0x0" ]]; then
        isFullScreen=$(xprop -id "$activeWindowId" | grep _NET_WM_STATE_FULLSCREEN)
    fi
    if [[ ! -z $isFullScreen ]]; then NPID=$(notify-send --hint string:image-path:$nIcon -a "System Mic" -per $NPID -t 2000 $txtStatus); fi
}

listen(){
    if [[ -z $DEBUG ]]; then
        scriptName=$(basename $0)
        others=($(pgrep ${scriptName::15}))
        for o in ${others[@]}; do
            if [[ $o -ne $$ ]]; then kill $o; fi
        done
    fi

    status

    inputSOURCES=($(pactl list short sources | grep input | cut -f1))
    grepInScr="source #${inputSOURCES[0]}"
    for scr in "${inputSOURCES[@]}"; do
        grepInScr="$grepInScr\\|source #$scr"
    done
    LANG=EN; pactl subscribe | while read -r event; do
        if echo "$event" | grep -q "$grepInScr"; then
            status
        fi
    done
}

$1