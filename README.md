# Rice tracker — "Doorway"

Linux Mint Cinnamon (X11) · laptop eDP 125% + ViewSonic 100%
Theme idea: open white door in an orange flower field under a teal → dusk-mauve sky.
Warm, dreamy, grainy. Dark base taken from the deep teal of the sky.

## Status

| #  | Component                    | Status   | Notes |
|----|------------------------------|----------|-------|
| 1  | Colour palette               | ✅ done  | see below — picked from the wallpaper |
| 2  | Wallpaper                    | ✅ done  | ~/Pictures/wallhaven-vp2l1m_1920x1080.png, zoom, both screens |
| 3  | Fonts                        | ✅ done  | Geist (UI) / GeistMono Nerd Font (mono) — kept |
| 4  | GTK theme (apps)             | ✅ done  | ~/.themes/Doorway, built by ~/rice/build-gtk.sh (recolours Mint-Y-Dark-Aqua) |
| 5  | Window borders               | ✅ done  | Doorway (GTK-drawn title bars, Mint-Y-Orange buttons) |
| 6  | Desktop shell (panel/menu)   | ✅ done  | ~/.themes/Doorway/cinnamon, built by ~/rice/build-shell.sh (recolours Mint-Y-Dark-Aqua + ~/rice/cinnamon.extra.css): translucent teal panel, rounded popups, orange accents, orange "today" |
| 7  | Icon theme                   | ✅ done  | Papirus-Dark, pale-orange folders — ~/rice/build-icons.sh re-points folder links in ~/.local/share/icons/Papirus |
| 8  | Cursor                       | ✅ done  | Bibata-Modern-Ice (white) |
| 9  | Panel layout                 | ✅ done  | floating islands, 40px, on the laptop (panel-on-laptop). Left: orange menu · workspaces 1-4 · window list. Centre: lunar calendar "Tue 27 Oct  17:52". Right: night light · keep awake (coffee cup, orange = on; icons in ~/.local/share/icons/hicolor/scalable/status/inhibit-*) · do-not-disturb bell (doorway-dnd@notrealqt, click = toggle, orange when silenced) · notification list (shows when there are some) │ bluetooth · drives · wifi · sound · battery. Mini stats dropped (card shows them). Tray filter: extension doorway-tray@notrealqt hides Update Manager, mintreport, process-monitor, NVIDIA Prime icons (apps still run). Old layout: ~/rice/panel-applets.before-B.txt · **Merges when maximised:** a maximised or tiled (top/left/right/quarter) window on the laptop's current workspace turns the strip solid #10252b (= window title-bar colour) and the islands melt into it, so panel + title bar / Firefox tabs read as one header; floating windows never count (extension doorway-solid@notrealqt + `.doorway-solid` rules in cinnamon.extra.css; mocks ~/rice/preview/panel-max-*.png, panel-case-*.png) |
| 10 | Login / lock screen          | ✅ done* | lock: .csstage css in ~/rice/gtk-3.0.extra.css, GeistMono clock, fixed centre, dimmed teal · login (slick-greeter): ~/rice/apply-login.sh — *needs `sudo bash ~/rice/apply-login.sh` once (re-run after rebuilding the GTK theme) |
| 11 | Terminal (kitty)             | ✅ done  | ~/.config/kitty/doorway.conf · opens 70x20 · no auto-fastfetch (`whale` shows the greeting) |
| 12 | Prompt (starship)            | ✅ done  | palette "doorway" in ~/.config/starship.toml |
| 13 | Fetch (fastfetch)            | ✅ done  | on demand only — type `whale` (no auto-run on new kitty). Greeting: humpback in a grid of small squares (contribution-graph style) swimming beside fastfetch — wake, spout, bubbles, light rays, fish. GIF ~/.config/kitty/whale-grid.gif built by ~/rice/whale/make_whale.py (20x44 px cells, 36x13 area); layout ~/.config/fastfetch/whale-grid.jsonc; played by ~/.local/bin/whale-greet (windows ≥68x16, else fastfetch without logo) |
| 14 | Terminal apps (btop, …)      | ✅ done  | ~/.config/btop/themes/doorway.theme |
| 15 | App launcher                 | ✅ done  | rofi grid: ~/.config/rofi/config.rasi (dpi 192 — screens render at 2x) + doorway-grid.rasi, Super+A → ~/rice/bin/doorway-launcher |
| 16 | Desktop widgets              | ✅ done  | network-admin conky card: system · link (wifi or wired + LLDP switch/port) · network (lan/gw/dns/wan/vpn/fw) · health (ms/loss/jitter via fping) · connections · memory (top 4 apps by RAM). Follows the panel: laptop top-right just under the panel (DOORWAY_HEAD from doorway-card; panel-on-laptop restarts it on monitor change). Super+M toggles. Alerts running. Needs lldpd iw ufw fping (installed). |
| 17 | Editor (VS Code)             | ✅ done  | Doorway colour theme (~/rice/vscode-doorway → doorway-theme.vsix, installed), GeistMono 14 / terminal 13, ligatures, smooth caret, custom title bar |
| 18 | Browser (Firefox)            | ✅ done  | userChrome.css / userContent.css + user.js in profile ym2kcaxo.default-release (copies in ~/rice/firefox): teal toolbars, tab strip #10252b with no separate title bar (matches the merged panel), orange line on the active tab, orange focused URL bar, dark new tab |
| 19 | Window behaviour             | ✅ done  | Super+1-4 go to workspace, Super+Shift+1-4 move window there (window-list Super+number launching turned off) · Super+←→↑↓ tile · Super+F maximise · Super+H minimise · Super+Q close · new windows centred · dialogs attached · animations fast |
| 20 | Dotfiles / backup            | ✅ done  | ~/rice is a git repo. `bash ~/rice/collect.sh` copies all configs into ~/rice/dotfiles + dumps Cinnamon settings (~/rice/dconf) + commits. Fresh install: packages.txt → restore.sh → apply-login.sh |

Other tweaks done: Vietnamese typing = fcitx5 + Unikey Telex (Super+Space EN/VI, ~/.config/fcitx5, Doorway theme ~/.local/share/fcitx5/themes/Doorway; old fcitx4 purged; GLFW_IM_MODULE=ibus in ~/.xsessionrc for kitty) · screenshots = Flameshot on Ctrl+Shift+S (~/rice/bin/doorway-shot → ~/Pictures/Screenshots) · kitty opens 70x20 · dark mode on, desktop icons on (laptop screen), auto-arrange off,
icon grid spacing 75%.

## 1 · Palette

Sampled from the wallpaper, then adjusted a little so text stays readable on the dark base.

| Role        | Hex       | From the picture |
|-------------|-----------|------------------|
| base (bg)   | `#0b1d22` | deep teal sky, darkened |
| surface     | `#12292f` | panels, sidebars |
| overlay     | `#1d3b42` | hover, selection bg |
| line        | `#2c4a50` | borders |
| muted       | `#7c9196` | comments, inactive text |
| text        | `#e8dfc6` | the door, softened |
| bright      | `#f2e5b8` | lit side of the door |
| teal        | `#4f9aa6` | upper sky (accent 2) |
| sky deep    | `#0d5e6c` | top of the sky |
| orange      | `#e39236` | flower petals (main accent) |
| amber       | `#d78615` | petals in the sun |
| rust        | `#a95411` | shaded petals |
| mauve       | `#b39aab` | dusk band near the horizon |
| olive       | `#9aa556` | leaves |
| red         | `#cd5c45` | errors (warm, fits the flowers) |
| blue        | `#6c9fc0` | links / info |

Terminal 16 colours (for kitty later):
black `#12292f` / `#2c4a50` · red `#cd5c45` / `#e07a62` · green `#9aa556` / `#b5bf72`
yellow `#d78615` / `#e9a94f` · blue `#6c9fc0` / `#8db7d2` · magenta `#b39aab` / `#cbb4c3`
cyan `#4f9aa6` / `#74b6c0` · white `#e8dfc6` / `#f2e5b8`

## 3 · Fonts

| Use                         | Font |
|-----------------------------|------|
| Interface, documents        | Geist 10.5 |
| Window titles               | Geist SemiBold 10.5 |
| Desktop icon labels         | Geist 10 (was "Inter", which isn't installed) |
| Monospace / kitty           | GeistMono Nerd Font (kitty 12.5) |
| Lock screen                 | Geist Thin / Light |
| Login screen                | Geist 11 |

## Change log

- 2026-10-27 — old "whale" rice reverted to stock Mint (kept kitty + fonts)
- 2026-10-27 — dark theme, desktop icons, fractional scaling
- 2026-10-27 — started "Doorway": wallpaper, palette, fonts unified on Geist
- 2026-10-27 — kitty, starship, fastfetch, btop recoloured; Doorway GTK + window theme;
  conky monitoring card (~/rice/conky, data from ~/rice/bin/doorway-stat), Super+M toggle,
  alerts (~/rice/bin/doorway-alerts: CPU ≥90°C 30s, battery <15%, internet down), both autostart
- 2026-10-27 — lunar calendar applet; panel kept on laptop screen
- 2026-10-27 — icons: Papirus-Dark + pale-orange folders; Doorway Cinnamon shell theme
  Note: Cinnamon crashed once in its screenshot
  code (17:43, unrelated to the theme) → fallback mate-panel appeared; fixed by restarting Cinnamon
- 2026-10-27 — cursor Bibata-Modern-Ice; lock screen themed; rofi grid launcher (Super+A; Super+Space
  stays the US/VN keyboard switch); card moved under the panel on the laptop.
- 2026-10-27 — fcitx5 Unikey Telex replaces ibus/fcitx4 + xkb vn; keyboard applet → fcitx tray "en/vi"; Flameshot Ctrl+Shift+S
- 2026-10-27 — cleanup: old whale rice archive, .pre-rice backups, mockups (still in git history), unused cursor copy removed
- 2026-10-27 — window behaviour (workspace/tiling keys), VS Code + Firefox themes, login screen script, git backup (collect.sh / restore.sh)
- 2026-10-27 — panel B islands with workspaces, keyboard, night light, keep awake, DND; tray icons filtered
- 2026-10-28 — conky card: vpn and fw on separate lines (a long VPN name + IP overlapped "fw")
- 2026-10-28 — panel merges with maximised/tiled windows (doorway-solid extension); Firefox tab strip → #10252b and its separate title bar turned off (browser.tabs.inTitlebar)
- 2026-10-28 — conky card moved left (gap_x 16 → 27): its right edge spilled 10px onto the ViewSonic; now lines up with the right edge of the panel's right island (x 3060)

## Files

| What | Where |
|---|---|
| GTK theme builder | ~/rice/build-gtk.sh → ~/.themes/Doorway |
| Monitoring card | ~/rice/conky/doorway.conf + doorway.lua |
| Card data helper | ~/rice/bin/doorway-stat |
| Card on/off | ~/rice/bin/doorway-card (Super+M) |
| Alerts | ~/rice/bin/doorway-alerts |
| Autostart | ~/.config/autostart/doorway-card.desktop, doorway-alerts.desktop, panel-on-laptop.desktop |
| Lunar calendar applet | ~/.local/share/cinnamon/applets/doorway-calendar@notrealqt (copy of calendar@cinnamon.org + lunar.js, Chinese calendar UTC+8) |
| Shell theme builder | ~/rice/build-shell.sh + ~/rice/cinnamon.extra.css → ~/.themes/Doorway/cinnamon |
| Icon folders colour | ~/rice/build-icons.sh [colour] (default paleorange) |
| Launcher | ~/rice/bin/doorway-launcher + ~/.config/rofi/ (Super+A) |
| Lock screen style | ~/rice/gtk-3.0.extra.css (appended by build-gtk.sh) |
| Panel islands CSS | bottom of ~/rice/cinnamon.extra.css (zones .panelLeft/.panelCenter/.panelRight) |
| Do-not-disturb applet | ~/.local/share/cinnamon/applets/doorway-dnd@notrealqt |
| Vietnamese input | ~/.config/fcitx5/ (profile, config, conf/unikey.conf, conf/classicui.conf) |
| Screenshot | ~/rice/bin/doorway-shot + ~/.config/flameshot/flameshot.ini (Ctrl+Shift+S) |
| Greeting whale | ~/rice/whale/make_whale.py → ~/.config/kitty/whale-grid.gif · ~/.local/bin/whale-greet |
| VS Code theme | ~/rice/vscode-doorway (theme json + vsix) |
| Firefox theme | ~/rice/firefox (copied into the profile) |
| Login screen | ~/rice/apply-login.sh (sudo) |
| Backup / restore | ~/rice/collect.sh · ~/rice/restore.sh · ~/rice/packages.txt · ~/rice/dconf/ · ~/rice/dotfiles/ |
| Tray icon filter | ~/.local/share/cinnamon/extensions/doorway-tray@notrealqt |
| Solid panel when maximised | ~/.local/share/cinnamon/extensions/doorway-solid@notrealqt |
| Menu button icon | ~/rice/assets/doorway-menu.svg |
| Panel stays on laptop | ~/rice/bin/panel-on-laptop (watches monitor changes, moves panel to eDP's index) |

## Plan (original build order — all done; mockups are in the git history)

Hardware notes: Ryzen (k10temp Tctl), AMD Vega iGPU (amdgpu edge), NVIDIA RTX 3050 dGPU
(only read via nvidia-smi when already awake — don't wake it), NVMe temp, BAT0, ASUS fan hwmon, wifi wlp3s0.

Build order:
1. kitty colours → Doorway
2. GTK / window / panel themes in Doorway colours
3. Panel: remove Update Manager tray icon; custom stats applet
   (↓↑ · CPU · AMD · NVI (zz when asleep) · SSD % · BAT; amber/red thresholds; click → btop)
4. Conky monitoring card (system, network, latency, connections, fans)
5. btop theme + alerts

Suggested extras (not yet chosen): fan RPM / ASUS profile · VPN / public-IP indicator ·
alerts (temp, battery, gateway down) · hotkey to toggle card · lock screen · VS Code theme
