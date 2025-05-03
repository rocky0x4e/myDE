#!/bin/bash

function backup {
    local f=$1
    if [[ -L $f ]]; then
        unlink "$f"
    else
        mv "$f" "${f}.bk" 2> /dev/null
    fi
}

echo "Installing configs..."
for f in config/*; do
    echo "    Installing $f"
    backup $HOME/.config/$(basename $f)
    ln -s "$(pwd)/$f" "$HOME/.config/"
done

echo "Installing bash tools..."
for f in tools/*; do
    echo "    Installing $f"
    backup $HOME/.local/bin/$(basename $f)
    ln -s "$(pwd)/$f" $HOME/.local/bin
done


echo "Installing icons..."
for f in icons/*; do
    echo "    Installing $f"
    backup $HOME/.local/share/icons/$(basename $f)
    ln -fs "$(pwd)/$f" $HOME/.local/share/icons/
done

cd rocky-py-tools
pip install -e . --force --break-system-packages

echo -e '!!! Final step, need root access to install this mod,
    Hit Ctrl + C to skip it but the clear ram script and the MMC refresh function will not work'

sudo -k
echo "$USER ALL=(ALL) NOPASSWD: /sbin/modprobe
$USER ALL=(ALL) NOPASSWD: /usr/bin/tee /proc/sys/vm/drop_caches" | sudo tee /etc/sudoers.d/myDE
