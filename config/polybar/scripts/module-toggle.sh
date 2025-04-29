#!/bin/bash

GAP=${GAP:-${WAIT:-${DELAY}}}
secret=$RANDOM
moduleList=( "$@" )
for m in ${moduleList[@]}; do
    lock="/tmp/polybar.module.${m}.lock"
    if [[ ! -f $lock ]]; then
        if [[ $GAP ]]; then echo $secret > "$lock"; fi
    else
        rm -f $lock
    fi
    polybar-msg action ${m} module_toggle
done

if [[ -z $GAP ]]; then
    exit 0
fi

sleep $GAP
for m in ${moduleList[@]}; do
    lock="/tmp/polybar.module.${m}.lock"
    check=$(cat "$lock")
    if [[ ! -z $check && $check -ne $secret ]]; then continue; fi
    if [[ -f $lock ]]; then
        rm -f $lock
        polybar-msg action ${m} module_toggle
    fi
done

