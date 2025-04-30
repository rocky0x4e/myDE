#!/bin/bash

SH_FILE_NAME=rocky-torrent.sh
SH_FILE_PATH=$HOME/.local/bin/$SH_FILE_NAME
DESKTOP_FILE=$HOME/.local/share/applications/rocky-torrent.desktop

echo "!!! Create transmission rpc client script"
cat << 'EOF' > $SH_FILE_PATH
#!/bin/bash

URL=https://rocky8x.sytes.net/transmission
transmission-remote "$URL" -a $1 -n rocky:pbdsN5FmuH2Zb%
notify-send "magnet link added to $URL"
EOF

echo "!!! Create desktop file"

cat << EOF > $DESKTOP_FILE
[Desktop Entry]
Name=Rocky torrent
Exec=$SH_FILE_NAME %u
Icon=transmission-icon
Type=Application
Terminal=false
MimeType=application/x-bittorrent;x-scheme-handler/magnet;
EOF

chmod +x $SH_FILE_PATH
chmod +x $DESKTOP_FILE

xdg-desktop-menu install $DESKTOP_FILE
echo "!!! DONE !!!"
