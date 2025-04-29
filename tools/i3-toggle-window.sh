#!/bin/bash

query=$1
toRun=$2
isRunning=$(i3-msg '['$query']' focus | jq ".[].success")

echo $isRunning
if [[ $isRunning == false ]]; then eval "$toRun &"; 
else i3-msg '['$query']' kill; fi