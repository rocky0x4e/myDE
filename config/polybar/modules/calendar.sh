#!/usr/bin/env bash

DATEFMT=${DATEFMT:-"+%a %B %d %H:%M"}
CAL=$(date "$DATEFMT")
IFS=' ' read -r -a CAL <<< "$CAL"
IFS=' ' read -r -a panel <<< "$colorPanel"

fontDay=${fontDay:-0}
fontDate=${fontDate:-0}
fontHour=${fontHour:-0}

ACTION_CAL="i3-toggle-window.sh 'class=Gnome-calendar' gnome-calendar"
ACTION_CLK="i3-toggle-window.sh 'class=org.gnome.clocks' gnome-clocks"

declare -A DAY_FG
DEFAULT_FG=${panel[1]:-#000000}
DAY_FG["Mon"]=${panel[0]:-#000000}
DAY_FG["Sat"]=${panel[2]:-#000000}
DAY_FG["Sun"]=${panel[2]:-#000000}


DAY=${CAL[0]}
MONTH=${CAL[1]::3}
DATE=${CAL[2]}
TIME=${CAL[3]}
hour=${TIME:0:2}
if [ $hour -ge 7 ] && [ $hour -lt 16 ] ; then TIME_COLOR="${DEFAULT_FG}"
else TIME_COLOR=${DAY_FG["Sun"]}; fi

DFG=${DAY_FG[$DAY]:-$DEFAULT_FG}
echo "%{A1:$ACTION_CAL:}%{F$DFG}%{T$fontDay}$DAY%{T-}%{F-} %{T$fontDate}$MONTH.$DATE%{T-}%{A} %{A1:$ACTION_CLK:}%{T$fontHour}%{F$TIME_COLOR}$TIME%{F-}%{T-}%{A}"
