#!/bin/bash

# Check for root
if [[ $EUID -ne 0 ]]; then
    echo "Please run as root (e.g., with sudo)."
    exit 1
fi

pid=$(notify-send -epa "Mem control" "Clearing pagecache, dentries, and inodes...")

# Sync filesystem first
sync

# Drop caches
echo 3 > /proc/sys/vm/drop_caches

notify-send -r $pid -ea "Mem control" "Memory cache cleared."
