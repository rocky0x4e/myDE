#!/bin/bash
# QBT_API_TOKEN and QBT_URL must be set as env var
r=$(curl -X POST \
  -H "Authorization: Bearer ${QBT_API_TOKEN}" \
  -F "urls=$1" \
  ${QBT_URL}/api/v2/torrents/add)
dunstify -a "Torrent handler" -t 3000 "$r" "$QBT_URL"

