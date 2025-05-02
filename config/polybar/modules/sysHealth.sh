#!/usr/bin/env bash

IFS=' ' read -r -a panel <<< "$colorPanel"

declare -A myColors
colorIndex=(90 45 0)
myColors[${colorIndex[0]}]=${panel[0]:-#000000}
myColors[${colorIndex[1]}]=${panel[1]:-#000000}
myColors[${colorIndex[2]}]=${panel[2]:-#000000}
font=${font:-0}

function cpuAvg {
    cpuLoad=$(cat /proc/loadavg | awk '{print $1}')
    for c in "${colorIndex[@]}"; do
        if (( $(echo "$cpuLoad > $c" | bc -l) )); then color=${myColors[$c]}; break; fi
    done
    echo -e "%{A1:i3-toggle-window.sh 'title=\"System Monitor\"' gnome-system-monitor:}%{F$color}%{F-} %{T$font}${cpuLoad}%%{T-}%{A}"
}

function memUsage {
    memData=$(cat /proc/meminfo | head -n6)
    total=$(echo "$memData" |  awk 'match($0, /^MemTotal:\s+([0-9]*) kB$/, ary) {print ary[1]}')
    # buffr=$(echo "$memData" |  awk 'match($0, /^Buffers:\s+([0-9]*) kB$/, ary) {print ary[1]}')
    # cache=$(echo "$memData" |  awk 'match($0, /^Cached:\s+([0-9]*) kB$/, ary) {print ary[1]}')
    # free_=$(echo "$memData" |  awk 'match($0, /^MemFree:\s+([0-9]*) kB$/, ary) {print ary[1]}')
    avail=$(echo "$memData" |  awk 'match($0, /^MemAvailable:\s+([0-9]*) kB$/, ary) {print ary[1]}')
    # swap_=$(echo "$memData" |  awk 'match($0, /^SwapCached:\s+([0-9]*) kB$/, ary) {print ary[1]}')
    used=$(( 100 - ($avail * 100 / $total ) ))

    for c in "${colorIndex[@]}"; do
        if [[ $used -gt $c ]]; then color=${myColors[$c]}; break; fi
    done

    echo -e "%{A1:showRamStat:}%{F$color}%{F-} %{T$font}${used}%%{T-}%{A}"
}

function thermal {
    t=$(($(cat /sys/class/thermal/thermal_zone0/temp) / 1000))
    tmpOffset=(0 30 0)
    for i in $(seq 0 2); do
        c=${colorIndex[$i]}
        offSet=${tmpOffset[$i]}
        if [[ $(( $t - $offSet )) -gt $c ]]; then color=${myColors[$c]}; break; fi
    done
    echo -e "%{F$color} %{F-}%{T$font}${t}°C%{T-}"
}

function main {
    echo -e "$(cpuAvg) $(memUsage) $(thermal)"
}

$1