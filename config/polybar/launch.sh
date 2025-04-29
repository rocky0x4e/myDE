#!/usr/bin/env bash

# export NVM_DIR="$HOME/.nvm"
# [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
# [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Terminate already running bar instances
# If all your bars have ipc enabled, you can use 
polybar-msg cmd quit
# Otherwise you can use the nuclear option:
# killall --quiet --signal 9 polybar

# Launch bar1 and bar2
echo "---" | tee -a /tmp/polybar1.log
polybar -r top 2>&1 | tee -a /tmp/polybar1.log & disown

echo "Bars launched..."
