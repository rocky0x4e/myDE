#!/bin/bash

interval=45
intervalCrit=5
battCrit=30
icSYS="\\0icon\\x1f"

battDataDir=~/.config/polybar/data/upower

IFS=' ' read -r -a panel <<< "$colorPanel"
icPlgFul="\ue55c";   colorPlgFul=${panel[3]:-#000000}
icPlgChg="\uf376";   colorPlgChg=${panel[2]:-#000000}
icPlgNoC="\ue55e";   colorPlgNoC=${panel[1]:-#000000}
ic____NA="\uf1e6";   color____NA=${panel[0]:-#000000}

sound=~/Music/sound/ding-36029.mp3


icIdx=(70 50 25 10 0)
declare -A icPer icColor devInfoByName devIconByName
icPer[${icIdx[0]}]="\uf240"; icColor[${icIdx[0]}]="#00843D"
icPer[${icIdx[1]}]="\uf241"; icColor[${icIdx[1]}]="#8ffe09"
icPer[${icIdx[2]}]="\uf242"; icColor[${icIdx[2]}]="#FFFF33"
icPer[${icIdx[3]}]="\uf243"; icColor[${icIdx[3]}]="#ff5555"
icPer[${icIdx[4]}]="\uf244"; icColor[${icIdx[4]}]="#FF0000"

batt=/sys/class/power_supply/BAT1
cord=/sys/class/power_supply/ADP1/online

battStat=$batt/status
battCap=$batt/capacity
dateFormat="+%Y-%m-%dT%H:%M:%S"

function detail {
    upDev=()
    while IFS= read -r line; do
        upDev+=("$line")
    done <<< $(upower -e)

    col1Data="Power cord${icSYS}flash\n"
    col2Data="plugged-in${icSYS}plugged-in\n"
    c1Max=8
    c2Max=10
    if [[ $(cat $cord) -eq 0 ]]; then
        col2Data="unplugged${icSYS}no-plug\n"
    fi
    for dev in "${upDev[@]}"; do
        pInfo=$(upower -i $dev)
        model=$(echo   "$pInfo" | awk 'match($0, /model:\s+([-_a-zA-Z0-9 ]*)$/, ary) {print ary[1]}')
        vendor=$(echo  "$pInfo" | awk 'match($0, /vendor:\s+([-_a-zA-Z0-9 ]*)$/, ary) {print ary[1]}')
        if [[ -z ${model:-$vendor} ]]; then continue; fi

        health=$(echo "$pInfo"  | awk 'match($0, /capacity:\s+(.*)[0-9]{2}%$/, ary) {print ary[1]}')
        type=$(echo   "$pInfo"  | awk 'match($0, /^\s+([-_a-zA-Z0-9]*)$/, ary) {print ary[1]}')
        icon=$(echo   "$pInfo"  | awk 'match($0, /icon-name:\s+(.*).*$/, ary) {print ary[1]}')
        icon=${icon//\'/}
        percent=$(echo "$pInfo" | awk 'match($0, /percentage:\s+([0-9]*%).*$/, ary) {print ary[1]}')
        state=$(echo  "$pInfo"  | awk 'match($0, /state:\s+([-_a-zA-Z]*)$/, ary) {print ary[1]}')
        state=${state//unknown/}
        state=${state//fully-charged/| full}

        if [[ -z $vendor ]]; then batName=$model; else batName="${model}_${vendor}"; fi

        batInfo="$percent"
        moreInf=${state}
        if [[ ! -z $health ]]; then moreInf+=" | <span color='#ff5555' font_size='32pt'></span>: $health%"; fi
        if [[ -z $moreInf ]]; then batInfo+="${icSYS}${icon}\n"
        else batInfo+=" $moreInf${icSYS}${icon}\n"; fi
        c2=$((${#percent} + ${#state} + ${#health} +4))

        devInfoByName[$batName]="$pInfo"
        devIconByName[$batName]="$type"
        col1Data+="${batName}${icSYS}${type}\n"
        col2Data+=$batInfo
        if [[ ${#batName} -gt $c1Max ]]; then c1Max=${#batName}; fi
        if [[ $c2 -gt $c2Max ]]; then c2Max=$c2; fi
    done
    c=$(($c1Max + $c2Max + 28 ))
    # notify-send -e -a "Simple Power Stats" "Power stats" "$powStats"
    col2Data="${col2Data%'\n'}"
    l=$(echo -e "$col2Data" | wc -l)
    select=$(echo -e "${col1Data}${col2Data}" | rofi \
        -icon-theme rofi -markup-rows -dmenu -no-custom -p "Power details" \
        -hover-select -theme overlays/center-dialog \
        -theme+inputbar+children '[ prompt ]' \
        -theme+window+width ${c}ch \
        -theme+listview+lines $l \
        -theme+listview+columns 2 )
    detailInfo="${devInfoByName[$select]}"
    if [[ -z $detailInfo ]]; then return; fi

    zenity --info --title="$select" --icon-name="${devIconByName[$select]}" --text="${detailInfo}"
}

function monitor {
    scriptName=$(basename $0)
    others=($(pgrep ${scriptName::15}))
    for o in ${others[@]}; do
        if [[ $o -ne $$ ]]; then kill $o; fi
    done

    while true; do
        chargeStat=$(cat $battStat)
        battPercent=$(cat $battCap)
        powCord=$(cat $cord) # value: 0/1
        if [[ $battPercent -lt $battCrit && $powCord -eq 0 ]]; then
            paplay $sound
            notify-send -e -a "Battery stats" "Battery low!!!" "Battery is at ${battPercent}%, please charge!!!" -u critical
            time=$intervalCrit
        else time=$interval; fi
        showIcon
        recordAllBatt >/dev/null 2>&1
        sleep $time
    done
}

function showIcon {
    chargeStat=$(cat $battStat)
    battPercent=$(cat $battCap)
    powCord=$(cat $cord) # value: 0/1
    case $powCord in
        1)
            case $chargeStat in
                "Full")
                    ic=$icPlgFul; color=$colorPlgFul
                    ;;
                "Charging")
                    ic=$icPlgChg; color=$colorPlgChg
                    ;;
                "Not charging")
                    ic=$icPlgNoC; color=$colorPlgNoC
                    ;;
            esac
            ;;
        0)
            for i in "${icIdx[@]}"; do
                if [[ $battPercent -gt $i ]]; then
                    ic=${icPer[$i]}
                    color=${icColor[$i]}
                    break
                fi
            done
            ;;
        *)
            ic=$ic____NA; color=$color____NA;
            ;;
    esac
    echo -e "%{F$color}$ic%{F-} "
}

function recordAllBatt {
    upDev=()
    while IFS= read -r line; do
        upDev+=("$line")
    done <<< $(upower -e)

    for dev in "${upDev[@]}"; do
        pInfo=$(upower -i $dev)
        model=$(echo   "$pInfo" | awk 'match($0, /model:\s+([-_a-zA-Z0-9 ]*)$/, ary) {print ary[1]}')
        vendor=$(echo  "$pInfo" | awk 'match($0, /vendor:\s+([-_a-zA-Z0-9 ]*)$/, ary) {print ary[1]}')
        if [[ -z ${model:-$vendor} ]]; then continue; fi
        serial=$(echo "$pInfo"  | awk 'match($0, /serial:\s+(.*)$/, ary) {print ary[1]}')
        nPath=$(echo   "$pInfo" | awk 'match($0, /native-path:\s+(.*)$/, ary) {print ary[1]}')
        percent=$(echo "$pInfo" | awk 'match($0, /percentage:\s+([0-9]*%).*$/, ary) {print ary[1]}')
        percent=${percent//%/}
        name=${vendor:-$model}_${serial:-$nPath}

        ### Notify if batt cap is low
        if [[ $percent -lt $battCrit ]]; then
            notify-send -e -a "Battery stats" "Battery low!!!" \
            "${name}'s battery is at ${percent}%, please charge!!!" -u critical
        fi

        file="$battDataDir/$name"
        file="${file// /_}.json"
        key=$(date $dateFormat)
        dates=($(jq '.history | keys[]' $file | sort -r)) || dates=()
        dataLen=${#dates[@]}

        if [[ $dataLen -eq 0 ]]; then
            newData='{"history":{"'$key'":'$percent'},"pluggedIn":""}'
        elif [[ $dataLen -eq 1 ]]; then
            newData=$(jq '.history."'$key'" = '$percent $file)
        elif [[ $dataLen -gt 1 ]]; then
            latest0=${dates[0]}
            latest1=${dates[1]}
            percent0=$(jq -r '.history.'${latest0} $file)
            percent1=$(jq -r '.history.'${latest1} $file)
            if [[ $percent != $percent0 ]]; then
                newData=$(jq '.history."'$key'" = '$percent $file)
            elif [[ $percent == $percent0 && $percent != $percent1 ]]; then
                newData=$(jq '.history."'$key'" = '$percent $file)
            elif [[ $percent == $percent0 && $percent == $percent1 ]]; then
                newData=$(jq 'del(.history.'$latest0')' $file)
                newData=$(echo "$newData" | jq '.history."'$key'" = '$percent)
            fi
        fi
        echo -e "$newData" | jq > "$file"
    done
}

function trimBattData {
    zCheckList=()
    for f in $battDataDir/*.json; do
        zCheckList+=(true $(basename $f))
    done
    select=$(zenity --list --title 'Trimming battery log' --width=600 --height=300 \
    --checklist --text="Select files to trim" --hide-header --column null --column file \
    ${zCheckList[@]})
    files=()
    while IFS='|' read -ra data; do
        for f in ${data[@]}; do
            files+=("$f")
        done
    done <<< "$select"

    for f in ${files[@]}; do
        f=$battDataDir/$f
        content=$(jq '.' $f )
        aWeekAgo=$(date --date="1 week ago" $dateFormat)
        dates=($(jq '.history | keys[]' $f ))
        toDel=""
        for d in ${dates[@]}; do
            if [[ $d < $aWeekAgo ]]; then
                toDel+=".history.${d}, "
            fi
        done
        if [[ -z $toDel ]]; then continue ; fi
        echo "$content" | jq 'del('"${toDel%', '}"')' > "$f"
    done
}

$1