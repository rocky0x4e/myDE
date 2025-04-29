#!/bin/bash


SESSION="tmuxControl"
action=$1
cmd=$2
appPath=$(echo "$cmd" | cut -d " " -f1)
appNameFull=$(basename "$appPath")
appName=${appNameFull::15}


function isRunning {
    if pgrep --exact $appName > /dev/null; then return 0; fi
    if tmux list-windows -t "$SESSION" -F '#{window_name}' | grep -Fxq "$appName"; then return 0; fi
    return 1
}

function flash {
    notify-send -ea tmuxControl "$1" "$2"
}

function startApp {
    if ! tmux has-session -t $SESSION > /dev/null; then tmux new-session -s $SESSION -d; fi
    if ! tmux list-windows -t "$SESSION" -F '#{window_name}' | grep -Fxq "$appName"; then
        tmux new-window -t $SESSION -n $appName -d
    fi
    tmux send-keys -t $SESSION:$appName "$cmd" C-m
    flash "Start $appName" "tmux session: $SESSION | window: $appName"
}

function stopApp {
    pkill $appName
    tmux send-keys -t $SESSION:$appName C-v
    tmux kill-window -t $SESSION:$appName
    flash "Stop $appName" "tmux session: $SESSION | window: $appName"
}

function choose {
    I='\x00icon\x1f'
    if isRunning; then
        select=$(echo -en "Stop${I}no\nRestart${I}refresh" | rofi -dmenu -icon-theme rofi \
            -p "$appNameFull" -theme+inputbar+children '[ prompt ]' \
            -theme overlays/center-dialog -theme+window+width 25ch )
        case $select in
            Stop) stopApp ;;
            Restart) stopApp; sleep 1; startApp ;;
        esac
    else startApp; fi
}

case $action in
    run|start) startApp ;;
    stop|kill) stopApp ;;
    check) isRunning ;;
    toggle) if isRunning ; then stopApp; else startApp; fi ;;
    choose) choose ;;
esac

