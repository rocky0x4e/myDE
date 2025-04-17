#!/bin/bash

prompt=${1:-"Are you sure?"}
I='\x00icon\x1f'
result=$(printf "Yes${I}yes\nNo${I}no" | rofi -dmenu -theme "overlays/center-yes-no" -icon-theme rofi -p "$prompt")

echo ${result:-No}