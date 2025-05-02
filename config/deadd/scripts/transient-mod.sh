#!/bin/bash
shopt -s extglob

tmp=$HOME/.config/deadd/tmp/log.json
echo debug > $tmp

# # Read notification from STDIN
noti=""
while read line
do
    noti=${noti}${line}
done < "${1:-/dev/stdin}"

nn='{"modify": {}, "match": {}}'

title=$(echo "$noti" | jq '.title')
body=$(echo "$noti" | jq '.body')
if [[ "$title" =~ "Data Copied" && "$body" =~ "&lt;EMPTY&gt;" ]]; then
    nn="{\"modify\": {
                \"transient\": true,
                \"app-name\": \"CopyQ\",
                \"timeout\": 1
            },
        \"match\":{}}"
elif [[ "$title" =~ "Text Copied" || "$title" =~ "Data Copied" ]]; then
    nn="{\"modify\": {
            \"transient\": true,
            \"app-name\": \"CopyQ\",
            \"timeout\": 2000
        },
    \"match\":{}}"
fi

echo "$noti" | jq >> $tmp
echo "$nn" | jq >> $tmp
echo "$nn"
