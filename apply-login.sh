#!/usr/bin/env bash
# Doorway rice — #10 login screen (LightDM slick-greeter). Run once with sudo:
#   sudo bash ~/rice/apply-login.sh
# The greeter runs as the 'lightdm' user before you log in, so it can't read ~/: wallpaper and
# theme are copied to system folders. Re-run after rebuilding the GTK theme. Undo: restore
# /etc/lightdm/slick-greeter.conf.pre-doorway.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "run with sudo"; exit 1; }
U=/home/notrealqt

install -Dm644 "$U/Pictures/wallhaven-vp2l1m_1920x1080.png" /usr/share/backgrounds/doorway/doorway.png

rm -rf /usr/share/themes/Doorway
cp -a "$U/.themes/Doorway" /usr/share/themes/Doorway
chown -R root:root /usr/share/themes/Doorway
chmod -R a+rX /usr/share/themes/Doorway

C=/etc/lightdm/slick-greeter.conf
[ -f "$C" ] && [ ! -f "$C.pre-doorway" ] && cp "$C" "$C.pre-doorway"
cat > "$C" <<'EOF'
# Doorway rice — login screen (written by ~/rice/apply-login.sh)
[Greeter]
background=/usr/share/backgrounds/doorway/doorway.png
background-color=#0b1d22
draw-user-backgrounds=false
draw-grid=false
theme-name=Doorway
icon-theme-name=Papirus-Dark
cursor-theme-name=Bibata-Modern-Ice
cursor-theme-size=24
font-name=Geist 11
clock-format=%a %d %b   %H:%M
show-hostname=true
enable-hidpi=auto
EOF
echo "login screen set — you'll see it next time you log out or reboot"
