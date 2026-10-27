#!/usr/bin/env bash
# Doorway rice — put the whole rice back on a fresh Linux Mint Cinnamon install.
#   1. sudo apt install $(cat ~/rice/packages.txt)      (fonts: Geist + GeistMono Nerd Font in ~/.local/share/fonts)
#   2. bash ~/rice/restore.sh
#   3. sudo bash ~/rice/apply-login.sh   then log out and back in
set -euo pipefail
R=$HOME/rice

# configs back into ~
cp -a "$R/dotfiles/." "$HOME/"
# Cinnamon settings (panel, shortcuts, themes, scaling, …)
dconf load /org/cinnamon/ < "$R/dconf/cinnamon.ini"
dconf load /org/nemo/ < "$R/dconf/nemo.ini"

# generated parts
[ -d "$HOME/.local/share/icons/Papirus" ] || cp -a /usr/share/icons/Papirus /usr/share/icons/Papirus-Dark "$HOME/.local/share/icons/"
bash "$R/build-gtk.sh"
bash "$R/build-shell.sh"
bash "$R/build-icons.sh"
python3 -I "$R/whale/make_whale.py"

# VS Code theme
command -v code >/dev/null && code --install-extension "$R/vscode-doorway/doorway-theme.vsix" >/dev/null 2>&1 || true
# Firefox (newest default-release profile; start Firefox once first so it exists)
FF=$(ls -d "$HOME"/.mozilla/firefox/*.default-release 2>/dev/null | head -1)
if [ -n "$FF" ]; then
  mkdir -p "$FF/chrome"
  cp "$R/firefox/user.js" "$FF/"
  cp "$R/firefox/userChrome.css" "$R/firefox/userContent.css" "$FF/chrome/"
fi
im-config -n fcitx5 2>/dev/null || true
echo "restored — now: sudo bash ~/rice/apply-login.sh, then log out and back in"
