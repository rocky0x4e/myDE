#!/bin/bash

entries=(
    "edit-select-all"        "Selection"
    "window_fullscreen"      "Window"
    "cs-screen"              "Whole screen"
)
SaveClip=0
SaveFile=2
SaveFile3=4
SaveClip3=6
appName=Screenshot
select=$(yad --list \
    --title="Select an Option" \
    --width=500 --height=300 \
    --center \
    --no-headers \
    --image-on-top \
    --column="Icon:IMG" \
    --column="Description" \
    "${entries[@]}" \
    --button="Clipboard!clipit-trayicon-panel":$SaveClip \
    --button="File!system-file-manager":$SaveFile \
    --button="File +3!system-file-manager":$SaveFile3 \
    --button="Clipboard +3!clipit-trayicon-panel":$SaveClip3
    )
button=$?

case "$button" in
    "$SaveFile")  
        saveTo="File"
        saveMode="~/Pictures/screenshots/$(date +%Y%m%d-%H%M%S).png"
        appName=R.Screenshot ;;
    "$SaveClip")
        saveTo="Clipboard"
        saveMode="| xclip -selection clipboard -t image/png" ;;
    "$SaveClip3")
        saveTo="Clipboard"
        saveMode="| xclip -selection clipboard -t image/png"
        sleep 3 ;;
    "$SaveFile3")
        saveTo="File under ~/Picture/screenshots"
        saveMode="~/Pictures/screenshots/$(date +%Y%m%d-%H%M%S).png"
        appName=R.Screenshot 
        sleep 3 ;;
esac

select=${select//|/}
case "$select" in
    "Window") maimMode='-i $(xdotool selectwindow)' ;;
    "Selection") maimMode='-s' ;;
    "Whole screen") maimMode='' ;;
esac

eval "maim $maimMode $saveMode" 

notify-send -t 3000 -ea $appName "Screenshot taken" "Saved to $saveTo"

