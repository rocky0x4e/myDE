#!/bin/bash

pid=$(notify-send -epa "Mem control" "Clearing pagecache, dentries, and inodes...")

# Sync filesystem first
sync

# Drop caches
echo 3 | sudo tee /proc/sys/vm/drop_caches

notify-send -r $pid -ea "Mem control" "Memory cache cleared."
