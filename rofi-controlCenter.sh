#!/bin/bash

PROMPT="System Control"
I='\x00icon\x1f'
W=
SEP="--------------------------------${I}zigzag"

if [[ -z $(pgrep xautolock) ]]; then
    SCREENLOCK="xAutolock: OFF"
    SCREENLOCK_IC=unprotected
else
    SCREENLOCK="xAutolock: ON"
    SCREENLOCK_IC=secure
fi

if [[ -z $(systemctl --user status Idle.timer | grep -o "Active: active") ]]; then
    AUTOSLEEP="Auto sleep: OFF"
    AUTOSLEEP_IC="green-tea"
    AUTOSLEEP_TOGGLE="systemctl --user start Idle.timer"
else
    AUTOSLEEP="Auto sleep: ON"
    AUTOSLEEP_IC="auto-sleep-on"
    AUTOSLEEP_TOGGLE="systemctl --user stop Idle.timer"
fi

function listAppImg {
    path="~/programs"
    menu=''
    for item in ~/programs/*; do
        if [[ $item =~ ".AppImage" ]]; then menu+="$(basename $item)${I}app\n"; fi
    done
    echo "$menu"
}

if tmuxControl.sh check mitmweb; then mitmMenu="Stop MITM"; else mitmMenu="Start MITM"; fi
if tmuxControl.sh check appium; then appiumMenu="Stop Appium"; else appiumMenu="Start Appium"; fi
if tmuxControl.sh check uxplay; then uxplayMenu="Stop UxPlay"; else uxplayMenu="Start UxPlay"; fi


OPTIONS="Deprecated, go use the python script !!!
$W Shutdown${I}system-shutdown
$W Reboot${I}system-reboot
$W Logout${I}system-log-out
Suspend${I}system-suspend
Lock${I}system-lock-screen
${SCREENLOCK}${I}${SCREENLOCK_IC}
${AUTOSLEEP}${I}${AUTOSLEEP_IC}
DNS SEC >>${I}ethernet
$SEP
HF builds${I}apk-64
Restmail${I}email
Pixel 6a${I}smartphone
Pixel 7pro${I}smartphone
AWS VPN${I}VPN
${mitmMenu}${I}hacker-activity
${appiumMenu}${I}appium
${uxplayMenu}${I}airplay
$SEP
Window inspector${I}inspection
$(listAppImg)
"

CHOICE=$(echo -e "$OPTIONS" | rofi -dmenu -i -theme "overlays/thin-side-bar" -icon-theme rofi -p "$PROMPT" -select Suspend)

if [[ "$CHOICE" =~ ^"${W} " ]]; then
    if [[ "$(rofi-yes-no.sh)" == "No" ]]; then exit 0; fi
fi

case "$CHOICE" in
    *Shutdown*) systemctl poweroff ;;
    *Reboot*)   systemctl reboot ;;
    *Suspend*)  systemctl suspend ;;
    *Logout*)   i3-msg exit ;;
    *Lock*)     ~/.config/i3/scripts/i3lock.sh locker ;;
    "$SCREENLOCK") /home/rocky/.config/i3/scripts/i3lock.sh toggle ;;
    "$AUTOSLEEP") eval "$AUTOSLEEP_TOGGLE" ;;
    "HF builds")  rofi-apkInstaller.sh /home/rocky/HF-data/builds ;;
    *.AppImage) chmod +x "$HOME/programs/$CHOICE"; "$HOME/programs/$CHOICE" ;;
    "Restmail") restmail.py ;;
    "DNS SEC >>") rofi-dnssec.sh ;;
    "$mitmMenu") tmuxControl.sh toggle mitmweb ;;
    "$appiumMenu") tmuxControl.sh toggle appium ;;
    "$uxplayMenu") tmuxControl.sh toggle "uxplay -a -nc -reg -nohold -reset 1" ;;
    "Pixel 6a") emulator @Pixel_6a_API_33 -feature -Vulkan -restart-when-stalled & ;;
    "Pixel 7pro") emulator @Pixel_7_Pro_API_35 -feature -Vulkan -restart-when-stalled & ;;
    "Window inspector")
        output=$(xprop | grep "WM_NAME\|WM_CLASS\|ROLE\|WINDOW_TYPE")
        yad --text-info --title="Window Properties" \
            --window-icon=stock_search \
            --width=1000 --height=300 \
            --wrap --center --button=Close:1 --editable=false \
            <<< "$output"
        ;;
esac
