#!/bin/bash

I="\x00icon\x1f"
DELMODE="Delete"
function installApk {
    file=$1
    adb start-server > /dev/null 2>&1
    devices=()
    while IFS=$'\n' read -r line; do
        if [[ -z $line ]]; then continue; fi
        devices+=("$line")
    done < <(adb devices)
    devices=("${devices[@]:1}")
    if [[ ${#devices[@]} == 1 ]]; then
        IFS=$'\t' read -r selects type <<< "${devices[0]}"
    else
        menuDevices=''
        for item in "${devices[@]}"; do
            IFS=$'\t' read -r serial type <<< "$item"
            if [[ $serial =~ "emulator-" ]]; then ic=android-emu; else ic=android-phone; fi
            menuDevices+="$serial${I}${ic}\n"
        done
        selects=$(echo -en "${menuDevices}" | rofi  -dmenu -multi-select -icon-theme rofi -theme overlays/thin-side-bar)
        IFS=$'\n' read -r -d '' -a selects <<< "$selects"
    fi
    for s in "${selects[@]}"; do
        echo -$s-
        r=$(adb -s "$s" install -d "$file" 2>&1)
        notify-send -e -a "APK installer" "Installing..." "$r"
    done
}

function browse {
    path="$1"
    items=()
    while IFS=$'\n' read -r line; do
        items+=("$line")
    done < <(ls -1 "$path")
    IFS=$'\n' sorted=($(sort -r <<<"${items[*]}"))

    folder="back${I}back\n"
    apkFiles=""
    for item in "${sorted[@]}"; do
        if [[ -d "$path/$item" ]]; then folder+="$item"${I}folder"\n"; fi
        if [[ "$item" =~ ".apk"$ ]]; then apkFiles+="$item"${I}apk-64"\n"; fi
    done

    select=$(echo -en "${folder}${apkFiles}" | rofi -dmenu -icon-theme rofi -select test -theme overlays/thin-side-bar)
    echo $select
}

#------------- MAIN ------------
path=$1
while [[ -d $path ]]; do
    select=$(browse $path)
    if [[ -z $select ]]; then exit 0; fi
    if [[ $select == 'back' ]]; then path=$(dirname $path);
    else path="$path/$select"; fi
done

if [[ $path =~ ".apk"$ ]]; then
    installApk $path
fi


