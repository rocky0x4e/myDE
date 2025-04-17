#!/usr/bin/env bash

interfaces=($(ip -o link show | awk -F': ' '{print $2}'))
IC="\\0icon\\x1f"
icSttYes="${IC}secure"
icStt_No="${IC}unprotected"

DNS_SEC_SETTINGS=$(resolvectl dnssec)
DNS_TLS_SETTINGS=$(resolvectl dnsovertls)

declare -A TOGGLE

menuInterFaces=""
for interface in "${interfaces[@]}"; do
    status1=$(echo "$DNS_SEC_SETTINGS" | grep "($interface)" | grep -o "yes\|no")
    if [[ -z $status1 ]]; then continue; fi
    status2=$(echo "$DNS_TLS_SETTINGS" | grep "($interface)" | grep -o "yes\|no")

    if [[ $status1 == "no" || $status2 == "no" ]]; then 
        TOGGLE[$interface]=yes
        ic="$icStt_No"
    else
        TOGGLE[$interface]=no
        ic="$icSttYes"
    fi
    menuInterFaces=${menuInterFaces}${interface}${ic}"\n"
done

selected=$(echo -en "${menuInterFaces}" | rofi \
        -icon-theme rofi -markup-rows -dmenu -no-custom -p "DNSSEC status" \
        -hover-select -theme overlays/center-dialog \
        -theme+inputbar+children '[ prompt ]' \
        -theme+window+width 20ch )
if [[ -z $selected ]]; then exit 0; fi
if [[ -z ${TOGGLE[$selected]} ]]; then exit 0; fi

pkexec bash -c \
"resolvectl dnsovertls $selected ${TOGGLE[$selected]};
resolvectl dnssec $selected ${TOGGLE[$selected]};
resolvectl flush-caches"