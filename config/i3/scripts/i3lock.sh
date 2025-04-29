#!/bin/bash
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

fileName=${0##*/}
thisScript="$SCRIPTPATH/${fileName}"
lockMinute=15 # minutes
notificationSecond=15 # seconds
lockImg=~/.config/i3/img/i3-lock.png
lockColor=0E1621
iconEnabled=~/programs/my-scripts/icons/secure.png
iconDisabled=~/programs/my-scripts/icons/unprotected.png

function flash {
    flashOff
    newId=$(notify-send -a Xautolock -ep "$@")
    echo $newId > ~/.tmp/last-lock-notifier-id
}

function flashOff {
    dID=$(cat ~/.tmp/last-lock-notifier-id)
    notify-send -a Xautolock -er $dID -t 1 " "
}

function disable {
    xautolock -exit
    flash --hint string:image-path:file:///$iconDisabled "XAutolock disabled"
}

function isEnable {
    if [[ -z $(pgrep xautolock) ]]; then
        echo false
    else
        echo true
    fi
}

function locker {
    flashOff
    xset dpms force off
    sleep 3
    i3lock -enfc $lockColor -i $lockImg
    # -n: not fork, to prevent xautolock from keep calling the notifier and locker when a locker is already running
    # must turn off the screen first otherwise the lock with -n will hold the script forever
}

function lockerFork {
    i3lock -efc $lockColor -i $lockImg
    sleep 5
    xset dpms force off
}

function notifier {
    flash --hint string:image-path:file:///$iconEnabled "Autolock" "Screen lock in 15s."
    paplay ~/Music/sound/ding-36029.mp3
}

function launcher {
    xautolock -exit
    sleep 1
    /usr/bin/xautolock -time $lockMinute -notify $notificationSecond -notifier "$thisScript notifier" -locker "$thisScript locker" &
}

function toggle {
    if [[ $(isEnable) == "true" ]]; then
        disable
    else
        flash --hint string:image-path:file:///$iconEnabled "XAutolock enabled"
        launcher
    fi
}

$1
