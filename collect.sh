#!/usr/bin/env bash
# Doorway rice — copy every config the rice uses into ~/rice/dotfiles (same paths as under ~),
# dump the Cinnamon settings, then commit. Run after any change:  bash ~/rice/collect.sh
# Generated things are NOT copied (rebuilt by restore.sh): ~/.themes/Doorway, the Papirus copy.
set -euo pipefail
R=$HOME/rice
D=$R/dotfiles
FF=$(ls -d "$HOME"/.mozilla/firefox/*.default-release 2>/dev/null | head -1)

FILES=(
  .bashrc .xsessionrc
  .config/kitty .config/starship.toml .config/fastfetch .config/rofi .config/fcitx5
  .config/btop/btop.conf .config/btop/themes/doorway.theme
  .config/flameshot/flameshot.ini
  .config/gtk-3.0/settings.ini .config/gtk-4.0/settings.ini
  .config/autostart/doorway-card.desktop .config/autostart/doorway-alerts.desktop
  .config/autostart/panel-on-laptop.desktop .config/autostart/fcitx5.desktop
  .config/cinnamon/spices
  .config/Code/User/settings.json
  .local/bin/whale-greet
  .local/share/cinnamon/applets/doorway-calendar@notrealqt
  .local/share/cinnamon/applets/doorway-dnd@notrealqt
  .local/share/cinnamon/extensions/doorway-tray@notrealqt
  .local/share/cinnamon/extensions/doorway-solid@notrealqt
  .local/share/fcitx5/themes/Doorway
  .local/share/icons/hicolor/scalable/status
  .icons/default/index.theme
)

rm -rf "$D"; mkdir -p "$D"
for f in "${FILES[@]}"; do
  [ -e "$HOME/$f" ] || { echo "skip (missing): $f"; continue; }
  mkdir -p "$D/$(dirname "$f")"
  cp -a "$HOME/$f" "$D/$f"
done
# Firefox profile files live under a random profile name; keep them in ~/rice/firefox
if [ -n "$FF" ]; then
  cp "$FF/user.js" "$FF/chrome/userChrome.css" "$FF/chrome/userContent.css" "$R/firefox/" 2>/dev/null || true
fi
# Cinnamon / desktop settings (panel layout, keybindings, themes, fonts, scaling, …)
mkdir -p "$R/dconf"
dconf dump /org/cinnamon/ > "$R/dconf/cinnamon.ini"
dconf dump /org/nemo/ > "$R/dconf/nemo.ini"
# packages the rice needs (for a fresh install)
cat > "$R/packages.txt" <<'EOF'
conky-all lm-sensors fping lldpd iw ufw btop kitty fastfetch starship
rofi flameshot fcitx5 fcitx5-unikey fcitx5-frontend-gtk3 fcitx5-frontend-gtk4 fcitx5-frontend-qt5 fcitx5-config-qt
papirus-icon-theme code wmctrl
EOF

cd "$R"
git add -A
if git diff --cached --quiet; then echo "nothing changed"; else
  git commit -q -m "rice: snapshot $(date +%F\ %H:%M)" && echo "committed: $(git log -1 --format=%h)"
fi
