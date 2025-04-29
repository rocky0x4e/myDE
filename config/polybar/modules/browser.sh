#!/bin/bash

BRAVE=brave-browser.desktop
GOOGLE=google-chrome.desktop
BROWSERS=($BRAVE $GOOGLE)
declare -A ICONS NAME PROCESSNAME WMCLASS INDEX BACKGR FOREGR

INDEX[$BRAVE]=0
NAME[$BRAVE]=Brave
PROCESSNAME[$BRAVE]=brave-browser
WMCLASS[$BRAVE]=Brave-browser
ICONS[$BRAVE]="\ue572"
FOREGR[$BRAVE]="#fff"
BACKGR[$BRAVE]="#e53238"

INDEX[$GOOGLE]=1
NAME[$GOOGLE]=Chrome
PROCESSNAME[$GOOGLE]="^chrome$"
WMCLASS[$GOOGLE]=Google-chrome
ICONS[$GOOGLE]="\uf268"
FOREGR[$GOOGLE]="#FFFF8D"
BACKGR[$GOOGLE]="#0f9d58"



function getCurrent {
    current=$(xdg-settings get default-web-browser)
    if [[ ${NAME[$current]} == "" ]]; then 
        xdg-settings set default-web-browser ${BROWSERS[0]}
        current=${BROWSERS[0]}
    fi
    echo $current
}

function notify {
    msg=$1; time=$2; time=${time:=2000}
    notify-send -e -t $time "$msg"
}

current=$(getCurrent)

case $1 in
    switch)
        current=$(getCurrent)
        indeoxOther=$((1 - ${INDEX[$current]}))
        other=${BROWSERS[$indeoxOther]}
        xdg-settings set default-web-browser $other
        notify "Default browser ${NAME[$current]} -> ${NAME[$other]}"
        current=$other
        ;;
    open)
        current=$(getCurrent)
        if [[ -z $(pgrep ${PROCESSNAME[$current]}) ]]; then
            notify "Launching ${NAME[$current]}"
            i3-msg -q "exec --no-startup-id dex /usr/share/applications/$current"
        else
            notify "Focusing ${WMCLASS[$current]}"
            i3-msg -q "[class=\"${WMCLASS[$current]}\"] focus"
        fi
        ;;
esac

echo -e "%{B${BACKGR[$current]}}%{F${FOREGR[$current]}}${ICONS[$current]}%{F-}%{B-}"
