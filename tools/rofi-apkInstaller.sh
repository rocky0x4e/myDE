#!/bin/bash

I="\x00icon\x1f"
DELMODE="Delete"
function installApk {
    local file=$1
    if [[ ! $file =~ patched.apk && ! -f ${file//.apk/}-patched.apk ]]; then
        select=$(echo -en "Patch${I}bandage\nPatch and Install${I}bandage\nInstall${I}download" | rofi -dmenu -icon-theme rofi -theme overlays/center-dialog \
            -p "Patch for MITM snooping or just install?" -theme+inputbar+children '[ prompt ]') || exit 0
        if [[ $select =~ "Patch" ]]; then
            local pid=$(notify-send -pet 0 "Patching, wait..." "$(basename $file) for MITM snooping")
            apk-mitm $file 2>&1 | tee ~/tmp/debug.log
            if [[ $? != 0 ]]; then notify-send -er $pid -t 2000 "Fail to patch" ; exit 1; fi
            notify-send -er $pid -t 3000 "Pathching" "$(basename $file) Done"
            file=${file/%.apk/-patched.apk}
        fi
        if ! [[ $select =~ "Install" ]]; then return; fi
    fi
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
        r=$(adb -s "$s" install -d "$file" 2>&1)
        notify-send -e -a "APK installer" "Installing ..." "$(basename $file) -> $s\n$r"
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
    openF="Open folder${I}open-folder"
    apkFiles=""
    for item in "${sorted[@]}"; do
        if [[ -d "$path/$item" ]]; then folder+="$item"${I}folder"\n"; fi
        if [[ "$item" =~ ".apk"$ ]]; then apkFiles+="$item"${I}apk-64"\n"; fi
    done

    select=$(echo -en "${folder}${apkFiles}${openF}" | rofi -dmenu -icon-theme rofi -select test -theme overlays/thin-side-bar)
    echo $select
}

#------------- MAIN ------------
path=$1
while [[ -d $path ]]; do
    select=$(browse $path)
    if [[ -z $select ]]; then exit 0; fi
    case $select in
        "back") path=$(dirname $path);;
        "Open folder") xdg-open $path; exit 0;;
        *) path="$path/$select";;
    esac
done

if [[ $path =~ ".apk"$ ]]; then
    installApk $path
fi


