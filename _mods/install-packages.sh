#!/bin/bash

echo "options hid_apple fnmode=2" | sudo tee /etc/modprobe.d/keyboard.conf
echo rtsx_pci_sdmmc | sudo tee /etc/modules-load.d/sdcard-reader.conf
echo "options mt7921e disable_aspm=1" | sudo tee /etc/modprobe.d/mt7921e.conf

# update system
sudo apt update && sudo apt upgrade -y

# install others
sudo apt install -y acpi sysstat htop geany zsh fonts-powerline fonts-font-awesome xclip nitrogen fcitx-unikey maim xautolock simplescreenrecorder jq transmission-cli ffmpeg mpv python3-tk brightnessctl copyq xprintidle

# use zsh
chsh -s $(which zsh)

# install brave
sudo apt install -y curl
sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" | sudo tee /etc/apt/sources.list.d/brave-browser-release.list
sudo apt update
sudo apt install -y brave-browser


cat << 'EOF' > /usr/lib/udev/rules.d/90-brightnessctl.rules
ACTION=="add", SUBSYSTEM=="backlight", RUN+="/bin/chgrp video /sys/class/backlight/%k/brightness"
ACTION=="add", SUBSYSTEM=="backlight", RUN+="/bin/chmod g+w /sys/class/backlight/%k/brightness"
ACTION=="add", SUBSYSTEM=="leds", RUN+="/bin/chgrp input /sys/class/leds/%k/brightness"
ACTION=="add", SUBSYSTEM=="leds", RUN+="/bin/chmod g+w /sys/class/leds/%k/brightness"
EOF
sudo usermod -aG video $USER
sudo usermod -aG input $USER

gio mime application/x-bittorrent rocky-torrent.desktop
gio mime application/vnd.android.package-archive rofi-apkInstaller.desktop

###############################################