# Doorway rice — #9 panel, option B (islands) with productivity add-ons, numbered for picking.
# python3 -I ~/rice/preview/make_panel_b2_mock.py  ->  panel-b2.png
import sys
sys.argv = ['x']
exec(open('/home/notrealqt/rice/preview/make_round2_mock.py').read().split("panes = [('A', 'Clean bar")[0])

LW, PH = 3072, 80
P22 = '/usr/share/icons/Papirus-Dark/22x22/'


def ico(name, s=34):
    for sub in ('panel', 'actions', 'status', 'apps', 'devices'):
        im = svg(f'{P22}{sub}/{name}.svg', s)
        if im:
            return im
    return None


strip = WALL.resize((LW, int(LW * 1080 / 1920))).crop((0, 0, LW, 200))
d = ImageDraw.Draw(strip)
marks = []          # (x, number) for the callouts
m, ih, y = 10, PH - 20, 0


def pill(x0, x1):
    shadow(strip, (x0, m, x1, m + ih), ih / 2, 10, 90)
    d.rounded_rectangle((x0, m, x1, m + ih), ih / 2, fill=C['base'] + (225,), outline=C['line'], width=2)


# left island: menu · workspaces · apps
APPS = ['nemo', 'firefox', 'kitty', 'google-chrome', 'code']
L1 = 14 + 92 + 4 * 46 + 30 + len(APPS) * 66
pill(14, L1)
d.ellipse((28, m + 10, 28 + ih - 20, m + ih - 10), fill=C['orange'])
d.ellipse((40, m + 22, 28 + ih - 32, m + ih - 22), outline=C['base'], width=4)
x = 104
for i in range(4):
    if i == 0:
        d.rounded_rectangle((x, m + 16, x + 38, m + ih - 16), 10, fill=C['orange'])
        d.text((x + 19, PH / 2), '1', fill=C['base'], font=F(22, 'SemiBold'), anchor='mm')
    else:
        d.text((x + 19, PH / 2), str(i + 1), fill=C['muted'] if i != 2 else C['text'], font=F(22), anchor='mm')
        if i == 2:
            d.ellipse((x + 16, m + ih - 12, x + 22, m + ih - 6), fill=C['muted'])
    x += 46
marks.append((104 + 92, 1))
d.line((x + 6, m + 16, x + 6, m + ih - 16), fill=C['line'], width=2)
x += 26
for i, n in enumerate(APPS):
    ic = app(n, 44)
    if i == 1:
        d.ellipse((x + 18, PH - 16, x + 26, PH - 8), fill=C['orange'])
    if ic: strip.alpha_composite(ic, (x, (PH - 44) // 2))
    x += 66

# centre island: clock
ct = 'Tue 27 Oct   17:52'
cw = d.textlength(ct, font=F(25, 'SemiBold')) + 64
pill(LW / 2 - cw / 2, LW / 2 + cw / 2)
d.text((LW / 2, PH / 2), ct, fill=C['bright'], font=F(25, 'SemiBold'), anchor='mm')

# right island: stats | VN | night · awake · bell | bt · wifi · sound · battery
fm = F(22, 'Regular', mono=True)
items = []
items.append(('stats', None))
items.append(('sep', None))
items.append(('kbd', None))
items += [('icon', 'redshift-status-on'), ('icon', 'caffeine-cup-empty'), ('icon', 'bell')]
items.append(('sep', None))
items += [('icon', 'bluetooth-active'), ('icon', 'network-wireless-signal-excellent'), ('icon', 'audio-volume-high'), ('icon', 'battery-080-charging')]
nums = {0: 3, 2: 2, 3: 4, 4: 5, 5: 6, 7: 7}


def stats_w():
    return width_of(d, False)


wsum = 30 + stats_w() + 26 + 2 + 26 + 56 + 3 * 52 + 26 + 2 + 26 + 4 * 52 + 20
R0 = LW - 14 - wsum
pill(R0, LW - 14)
x = R0 + 30
for k, (kind, val) in enumerate(items):
    if k in nums:
        marks.append((x + (stats_w() / 2 if kind == 'stats' else 17), nums[k]))
    if kind == 'stats':
        x = stats(d, x, PH / 2, False) + 26
    elif kind == 'sep':
        d.line((x, m + 16, x, m + ih - 16), fill=C['line'], width=2); x += 28
    elif kind == 'kbd':
        d.rounded_rectangle((x, m + 17, x + 46, m + ih - 17), 8, outline=C['muted'], width=2)
        d.text((x + 23, PH / 2), 'VN', fill=C['text'], font=F(17, 'SemiBold'), anchor='mm'); x += 56
    else:
        ic = ico(val)
        if ic: strip.alpha_composite(ic, (int(x), (PH - 34) // 2))
        x += 52

# callout badges under the bar
for cx, n in marks:
    d.line((cx, PH + 4, cx, PH + 34), fill=C['orange'], width=2)
    d.ellipse((cx - 22, PH + 34, cx + 22, PH + 78), fill=C['orange'])
    d.text((cx, PH + 56), str(n), fill=C['base'], font=F(24, 'Bold'), anchor='mm')

# ── page ──
W = LW + 80
page = Image.new('RGBA', (W, 1500), C['base'] + (255,))
pd = ImageDraw.Draw(page)
pd.text((40, 34), '#9 Panel B (islands) — productivity add-ons, numbered', fill=C['bright'], font=F(44, 'SemiBold'))
pd.text((40, 96), 'Whole laptop-width panel (40 px), then each island zoomed. Tell me which numbers to keep — default is all of them.',
        fill=C['muted'], font=F(26))
page.alpha_composite(strip, (40, 160))
pd.rounded_rectangle((39, 159, 40 + LW, 160 + 200), 10, outline=C['line'], width=2)
# zooms
zl = strip.crop((0, 0, int(L1) + 20, 130)).resize((int((L1 + 20) * 1.6), 208), Image.LANCZOS)
zr = strip.crop((int(R0) - 10, 0, LW, 130))
zr = zr.resize((int(zr.width * 1.6), 208), Image.LANCZOS)
page.alpha_composite(zl, (40, 400))
page.alpha_composite(zr, (W - 40 - zr.width, 400))

LEG = [
    ('1', 'Workspaces 1 2 3 4', 'separate desktops (e.g. work · study · chill). Ctrl+Alt+←/→ to switch; dot = has windows', 'built in'),
    ('2', 'Keyboard layout  US / VN', 'you switch with Super+Space; this shows which one is on, click to change', 'built in'),
    ('3', 'Mini stats  ↓↑ · CPU · BAT', 'turns amber / red when hot or low; click opens btop. Full details stay on the card', 'custom'),
    ('4', 'Night light', 'one click warm screen for the evening (Cinnamon night light)', 'built in'),
    ('5', 'Keep awake', 'stops the screen from sleeping/locking — downloads, labs, presentations', 'built in'),
    ('6', 'Do not disturb', 'bell; click to silence notifications, shows a dot when you have some', 'built in'),
    ('7', 'Bluetooth · Wi-Fi · Sound · Battery', 'what you asked to keep', 'kept'),
]
y = 650
for n, name, desc, tag in LEG:
    pd.ellipse((40, y, 88, y + 48), fill=C['orange'])
    pd.text((64, y + 24), n, fill=C['base'], font=F(26, 'Bold'), anchor='mm')
    pd.text((112, y + 4), name, fill=C['bright'], font=F(30, 'SemiBold'))
    pd.text((760, y + 8), desc, fill=C['text'], font=F(25))
    pd.text((W - 40, y + 8), tag, fill=C['muted'], font=F(24), anchor='ra')
    y += 76
y += 20
pd.line((40, y, W - 40, y), fill=C['line'], width=2)
y += 30
pd.text((40, y), 'Hidden from the panel', fill=C['orange'], font=F(28, 'SemiBold'))
pd.text((40, y + 48), 'Update Manager shield · Mint system reports · NVIDIA Prime "A" · drives icon (pops up only while a USB drive is plugged in)'
        ' — the apps still work, just no tray icon.', fill=C['text'], font=F(25))
pd.text((40, y + 92), 'Clock shortened to  Tue 27 Oct  17:52  — click still opens the lunar calendar.', fill=C['text'], font=F(25))
page = page.crop((0, 0, W, y + 150))
page.convert('RGB').save(OUT + 'panel-b2.png')
print('ok')
