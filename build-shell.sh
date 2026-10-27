#!/usr/bin/env bash
# Doorway rice — build the Cinnamon shell theme (panel, menus, popups, calendar, OSDs)
# into ~/.themes/Doorway/cinnamon by re-colouring Mint-Y-Dark-Aqua's, then appending
# ~/rice/cinnamon.extra.css (rounded popups, orange accents). Look: ~/rice/preview/shell.png
# Re-run after Mint updates its themes:  bash ~/rice/build-shell.sh
set -euo pipefail
SRC=/usr/share/themes/Mint-Y-Dark-Aqua/cinnamon
DST=$HOME/.themes/Doorway/cinnamon

# Mint-Y-Dark greys -> Doorway teals, Mint aqua -> deep teal, reds/oranges -> palette
recolor() {
  sed -E \
    -e 's/#222226\b/#12292f/gI'  -e 's/#303036\b/#1d3b42/gI'  -e 's/#2a2a2f\b/#163038/gI' \
    -e 's/#29292e\b/#10252b/gI'  -e 's/#303030\b/#12292f/gI'  -e 's/#38383e\b/#22424a/gI' \
    -e 's/#3c3c44\b/#2c4a50/gI'  -e 's/#44444c\b/#2f5057/gI'  -e 's/#494951\b/#35555b/gI' \
    -e 's/#c3c3c3\b/#c9c2ab/gI'  -e 's/#e1e1e1\b/#e8dfc6/gI'  -e 's/#ffffff\b/#f2e5b8/gI' \
    -e 's/#1f9ede\b/#2e7682/gI' \
    -e 's/#f04a50\b|#fc4138\b|#c01c28\b/#cd5c45/gI' -e 's/#d61f2d\b/#a94a37/gI' -e 's/#f27835\b/#d78615/gI' \
    -e 's/rgba\(29, 29, 33, /rgba(11, 29, 34, /g' \
    -e 's/rgba\(34, 34, 38, /rgba(18, 41, 47, /g' \
    -e 's/rgba\(48, 48, 54, /rgba(29, 59, 66, /g' \
    -e 's/rgba\(60, 60, 68, /rgba(44, 74, 80, /g' \
    -e 's/rgba\(225, 225, 225, /rgba(232, 223, 198, /g' \
    -e 's/rgba\(255, 255, 255, /rgba(232, 223, 198, /g' \
    -e 's/rgba\(31, 158, 222, /rgba(46, 118, 130, /g' \
    -e 's/rgba\(252, 65, 56, /rgba(205, 92, 69, /g' \
    "$1"
}

rm -rf "$DST"; mkdir -p "$DST"
recolor "$SRC/cinnamon.css" > "$DST/cinnamon.css"
cat "$HOME/rice/cinnamon.extra.css" >> "$DST/cinnamon.css"
# switches, checkboxes, arrows, window-list marks are SVGs with the same colours
for d in common-assets dark-assets; do
  (cd "$SRC" && find "$d" -type d) | while read -r sub; do mkdir -p "$DST/$sub"; done
  (cd "$SRC" && find "$d" -type f) | while read -r f; do
    case $f in *.svg) recolor "$SRC/$f" > "$DST/$f" ;; *) cp "$SRC/$f" "$DST/$f" ;; esac
  done
done
cp "$SRC/thumbnail.png" "$DST/"

gsettings set org.cinnamon.theme name 'Doorway'
echo "built $DST and applied it"
