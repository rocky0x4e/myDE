#!/bin/bash

for f in config/*; do
    if [[ $FORCE == "yes"]]; then
        unlink $HOME/.config/$(basename $f)
        rm -Rf $HOME/.config/$(basename $f)
    fi
    ln -s "$(pwd)/$f" $HOME/.config/
done

for f in tools/*; do
    ln -fs "$(pwd)/$f" $HOME/.local/bin
    # unlink $HOME/.config/$(basename $f)
done

