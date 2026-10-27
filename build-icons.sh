#!/usr/bin/env bash
# Doorway rice — icon theme: Papirus-Dark with pale-orange folders (option B, ~/rice/preview/icons.png).
# Works on the user copy in ~/.local/share/icons/Papirus (overrides the system one, no sudo).
# Papirus picks its folder colour through symlinks such as folder.svg -> folder-grey.svg;
# this re-points every one of them to the chosen colour, the way papirus-folders does.
# Usage: bash ~/rice/build-icons.sh [colour]   (default paleorange; e.g. orange, teal, grey)
set -euo pipefail
COLOR=${1:-paleorange}
T=$HOME/.local/share/icons/Papirus
# current colour = whatever folder.svg points at now (grey, left over from the whale rice)
OLD=$(readlink "$T/64x64/places/folder.svg" | sed -E 's/^folder-([a-z]+)\.svg$/\1/')
[ "$OLD" = "$COLOR" ] && { echo "already $COLOR"; }
n=0
while IFS= read -r link; do
  name=$(basename "$link")
  # skip the colour variants' own links (folder-grey-*.svg, user-grey-*.svg)
  [[ $name =~ ^(folder|user)-$OLD[-.] ]] && continue
  tgt=$(readlink "$link")
  new=$(echo "$tgt" | sed -E "s/^(folder|user)-$OLD(-|\.svg)/\1-$COLOR\2/")
  [ "$new" = "$tgt" ] && continue
  [ -e "$(dirname "$link")/$new" ] || continue
  ln -sfn "$new" "$link"; n=$((n + 1))
done < <(find "$T" "$T-Dark" -path "*/places/*" -type l)
gtk-update-icon-cache -qf "$T" 2>/dev/null || true
gtk-update-icon-cache -qf "$T-Dark" 2>/dev/null || true
gsettings set org.cinnamon.desktop.interface icon-theme 'Papirus-Dark'
gsettings set org.gnome.desktop.interface icon-theme 'Papirus-Dark' 2>/dev/null || true
echo "re-pointed $n folder links to $COLOR; icon theme = Papirus-Dark"
