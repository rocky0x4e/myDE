#!/bin/bash

I="\x00icon\x1f"
DELMODE="Delete"
function installApk {
    file=$1
    adb start-server > /dev/null 2>&1
    items=()
    while IFS=$'\n' read -r line; do
        if [[ -z $line ]]; then continue; fi
        items+=("$line")
    done < <(adb devices)
    items=("${items[@]:1}")
    menu=''
    for item in "${items[@]}"; do
        IFS=$'\t' read -r serial type <<< "$item"
        if [[ $serial =~ "emulator-" ]]; then ic=android-emu; else ic=android-phone; fi
        menu+="$serial${I}${ic}\n"
    done


    selects=$(echo -en "${menu}" | rofi  -dmenu -multi-select -icon-theme rofi -theme overlays/thin-side-bar)
    IFS=$'\n' read -r -d '' -a selects <<< "$selects"
    for s in "${selects[@]}"; do
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

    folder="back${I}back\n"
    apkFiles=""
    for item in "${items[@]}"; do
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


