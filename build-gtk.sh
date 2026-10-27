#!/usr/bin/env bash
# Doorway rice — build ~/.themes/Doorway (GTK 2/3/4 + libadwaita + window buttons)
# by re-colouring Mint-Y-Dark-Aqua onto the Doorway palette.
# Re-run after Mint updates its themes:  bash ~/rice/build-gtk.sh
set -euo pipefail
SRC=/usr/share/themes/Mint-Y-Dark-Aqua
DST=$HOME/.themes/Doorway

# palette: base #0b1d22 · surface #12292f · overlay #1d3b42 · line #2c4a50
#          muted #7c9196 · text #e8dfc6 · bright #f2e5b8
#          accent (selection) deep teal #2e7682 · teal #4f9aa6 · orange #e39236
recolor() {
  sed -E \
    -e 's/#202023\b/#0f2329/gI'  -e 's/#2e2e33\b/#12292f/gI'  -e 's/#222226\b/#10252b/gI' \
    -e 's/#2c2c31\b/#163038/gI'  -e 's/#18181b\b/#091619/gI'  -e 's/#33333[89]\b/#1d3b42/gI' \
    -e 's/#3f3f46\b/#2c4a50/gI'  -e 's/#46464e\b/#35555b/gI'  -e 's/#27272b\b/#13282e/gI' \
    -e 's/#343439\b/#1c383f/gI'  -e 's/#353535\b/#1c383f/gI'  -e 's/#373737\b/#1f3d44/gI' \
    -e 's/#4c4c50\b/#3a585e/gI'  -e 's/#616166\b/#5f777c/gI'  -e 's/#676767\b/#5f777c/gI' \
    -e 's/#949498\b/#7c9196/gI'  -e 's/#080808\b/#061114/gI' \
    -e 's/#dadada\b|#dbdbdb\b|#e1e1e1\b/#e8dfc6/gI' \
    -e 's/#ffffff\b/#f2e5b8/gI' \
    -e 's/#1f9ede\b/#2e7682/gI'  -e 's/#197eb1\b/#25626c/gI' \
    -e 's/#8fcfef\b|#9ad3f0\b/#4f9aa6/gI' -e 's/#d2ecf8\b|#ddf0fa\b/#9cc7cd/gI' \
    -e 's/#f04a50\b|#fc4138\b|#ec1b22\b|#ff4d4d\b/#cd5c45/gI' \
    -e 's/#f4797e\b/#e07a62/gI'  -e 's/#aa3936\b/#9a3f2e/gI' \
    -e 's/#f27835\b/#d78615/gI' \
    -e 's/#6db442\b|#73d216\b/#9aa556/gI' -e 's/#568f34\b/#7a8540/gI' -e 's/#88c663\b/#b5bf72/gI' \
    -e 's/#5294e2\b/#6c9fc0/gI' \
    -e 's/rgba\(255, 255, 255, /rgba(232, 223, 198, /g' \
    -e 's/rgba\(219, 219, 219, /rgba(232, 223, 198, /g' \
    -e 's/rgba\(31, 158, 222, /rgba(46, 118, 130, /g' \
    "$1"
}

mkdir -p "$DST"
for d in gtk-3.0 gtk-4.0 libadwaita-1.5 libadwaita-1.7; do
  [ -d "$SRC/$d" ] || continue
  rm -rf "${DST:?}/$d"; mkdir -p "$DST/$d"
  [ -d "$SRC/$d/assets" ] && ln -s "$SRC/$d/assets" "$DST/$d/assets"
  for f in "$SRC/$d"/*.css; do recolor "$f" > "$DST/$d/$(basename "$f")"; done
  [ -f "$HOME/rice/$d.extra.css" ] && cat "$HOME/rice/$d.extra.css" >> "$DST/$d/gtk.css"
done
ln -sfn "$SRC/gtk-2.0" "$DST/gtk-2.0"
# window buttons: Mint-Y-Orange icons (orange on hover, matches the flowers)
ln -sfn /usr/share/themes/Mint-Y-Orange/metacity-1 "$DST/metacity-1"

cat > "$DST/index.theme" <<'EOF'
[Desktop Entry]
Type=X-GNOME-Metatheme
Name=Doorway
Comment=Teal dusk + orange flowers, matched to the door wallpaper
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=Doorway
MetacityTheme=Doorway
IconTheme=Papirus-Dark
CursorTheme=Bibata-Modern-Ice
ButtonLayout=:minimize,maximize,close
EOF
echo "built $DST"
