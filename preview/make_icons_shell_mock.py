# Doorway rice — mockups for #7 icons and #6 desktop shell.
# python3 -I ~/rice/preview/make_icons_shell_mock.py  ->  icons.png, shell.png
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GdkPixbuf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

K = 2
OUT = '/home/notrealqt/rice/preview/'
FS = '/home/notrealqt/.local/share/fonts/'
C = dict(base=(11, 29, 34), surface=(18, 41, 47), overlay=(29, 59, 66), line=(44, 74, 80), muted=(124, 145, 150),
         text=(232, 223, 198), bright=(242, 229, 184), teal=(79, 154, 166), sel=(46, 118, 130), orange=(227, 146, 54),
         # stock Mint-Y-Dark-Aqua
         m_bg=(48, 48, 54), m_bg2=(34, 34, 38), m_hover=(60, 60, 68), m_text=(225, 225, 225), m_acc=(31, 158, 222))


def font(size, weight='Regular'):
    import glob
    for pat in (f'{FS}**/Geist-{weight}.*tf', f'{FS}**/Geist*{weight}*.*tf', '/usr/share/fonts/**/DejaVuSans.ttf'):
        hits = sorted(glob.glob(pat, recursive=True))
        if hits:
            return ImageFont.truetype(hits[0], int(size * K))


def icon(path_or_name, size, theme=None):
    if theme:
        it = Gtk.IconTheme.new()
        it.set_custom_theme(theme)
        info = it.lookup_icon(path_or_name, size * K, 0)
        path = info.get_filename() if info else None
    else:
        path = path_or_name
    if not path:
        return None
    pb = GdkPixbuf.Pixbuf.new_from_file_at_size(path, size * K, size * K)
    if not pb.get_has_alpha():
        pb = pb.add_alpha(False, 0, 0, 0)
    return Image.frombytes('RGBA', (pb.get_width(), pb.get_height()), pb.get_pixels(), 'raw', 'RGBA', pb.get_rowstride())


# ─────────────────────────── icons.png ───────────────────────────
P = '/usr/share/icons/Papirus/64x64/'
LABELS = ['Home', 'Downloads', 'Documents', 'Pictures', 'folder', 'Firefox', 'VS Code', 'kitty', 'Files', 'btop']


def papirus(col):
    return [P + f'places/user-{col}-home.svg', P + f'places/folder-{col}-download.svg',
            P + f'places/folder-{col}-documents.svg', P + f'places/folder-{col}-pictures.svg',
            P + f'places/folder-{col}.svg'] + [P + f'apps/{a}.svg' for a in ('firefox', 'code', 'kitty', 'nemo', 'btop')]


def mint(theme):
    names = ['user-home', 'folder-download', 'folder-documents', 'folder-pictures', 'folder',
             'firefox', 'code', 'kitty', 'nemo', 'btop']
    return [(n, theme) for n in names]


OPTIONS = [
    ('A', 'Papirus-Dark · orange folders', 'recommended — folder orange is almost exactly the flower orange', papirus('orange')),
    ('B', 'Papirus-Dark · pale-orange folders', 'softer, closer to the cream door', papirus('paleorange')),
    ('C', 'Papirus-Dark · teal folders', 'quiet, blends with the sky', papirus('teal')),
    ('D', 'Mint-Y-Sand (now)', 'stock Mint, flat sand folders', mint('Mint-Y-Sand')),
]

IS, GAP, PAD, ROWH = 48, 34, 28, 132
W = PAD * 2 + len(LABELS) * (IS + GAP) - GAP + 20
H = 70 + len(OPTIONS) * ROWH + 10
img = Image.new('RGBA', (W * K, H * K), C['base'] + (255,))
d = ImageDraw.Draw(img)
d.text((PAD * K, 22 * K), '#7 Icon theme — pick one', fill=C['bright'], font=font(18, 'SemiBold'))
y = 70
for key, name, note, items in OPTIONS:
    d.rounded_rectangle((16 * K, y * K, (W - 16) * K, (y + ROWH - 14) * K), 12 * K, fill=C['surface'], outline=C['line'], width=K)
    d.text(((PAD) * K, (y + 12) * K), f'{key}  {name}', fill=C['orange'] if key == 'A' else C['text'], font=font(13, 'SemiBold'))
    d.text(((PAD) * K, (y + 30) * K), note, fill=C['muted'], font=font(10.5))
    x = PAD + 10
    for it, label in zip(items, LABELS):
        im = icon(it[0], IS, it[1]) if isinstance(it, tuple) else icon(it, IS)
        if im:
            img.alpha_composite(im, (x * K, (y + 52) * K))
        f = font(9)
        tw = d.textlength(label, font=f) / K
        d.text(((x + IS / 2 - tw / 2) * K, (y + 52 + IS + 4) * K), label, fill=C['muted'], font=f)
        x += IS + GAP
    y += ROWH
img.convert('RGB').save(OUT + 'icons.png')

# ─────────────────────────── shell.png ───────────────────────────
WP = Image.open('/home/notrealqt/Pictures/wallhaven-vp2l1m_1920x1080.png').convert('RGBA')
SW, SH = 960, 470


def shell(doorway):
    bg = WP.crop((0, 0, 1920, 940)).resize((SW * K, SH * K))
    ov = Image.new('RGBA', bg.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    if doorway:
        pbg, mbg, hover, txt, mut, acc, line = C['base'] + (235,), C['surface'] + (245,), C['overlay'], C['text'], C['muted'], C['orange'], C['line']
    else:
        pbg, mbg, hover, txt, mut, acc, line = C['m_bg2'] + (255,), C['m_bg'] + (255,), C['m_hover'], C['m_text'], (160, 160, 165), C['m_acc'], (70, 70, 78)
    R = 10 if doorway else 3

    # panel
    PH = 36
    d.rectangle((0, 0, SW * K, PH * K), fill=pbg)
    if doorway:
        d.line((0, PH * K, SW * K, PH * K), fill=line + (255,), width=K)
    menu_icon = icon('/usr/share/icons/Papirus/64x64/apps/linuxmint-logo-ring.svg' if False else '', 1) if False else None
    d.rounded_rectangle((8 * K, 6 * K, 32 * K, 30 * K), 6 * K, fill=acc + (255,) if doorway else (0, 0, 0, 0))
    d.ellipse((13 * K, 11 * K, 27 * K, 25 * K), outline=(C['base'] if doorway else C['m_acc']) + (255,), width=2 * K)
    # window list
    for i, (n, active) in enumerate([('kitty', True), ('Firefox', False), ('Files', False)]):
        x0 = 44 + i * 120
        if active:
            d.rounded_rectangle((x0 * K, 5 * K, (x0 + 112) * K, 31 * K), (6 if doorway else 2) * K, fill=hover + (255,))
            d.rectangle(((x0 + 30) * K, 31 * K if not doorway else 29 * K, (x0 + 82) * K, (33 if not doorway else 31) * K), fill=acc + (255,))
        d.text(((x0 + 12) * K, 10 * K), n, fill=txt if active else mut, font=font(11))
    # clock (center)
    ck = 'Tue 27 Oct  14:30'
    f = font(11.5, 'SemiBold' if doorway else 'Regular')
    d.text(((SW / 2) * K - d.textlength(ck, font=f) / 2, 9.5 * K), ck, fill=txt, font=f)
    # tray
    for i, s in enumerate(['wifi', 'vol', 'bat 82%']):
        d.text(((SW - 170 + i * 46) * K, 10 * K), s, fill=mut, font=font(10))

    # menu popup (left)
    mx, my, mw, mh = 8, PH + 8, 330, 380
    if doorway:
        sh = Image.new('RGBA', bg.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle(((mx + 2) * K, (my + 6) * K, (mx + mw + 2) * K, (my + mh + 6) * K), R * K, fill=(0, 0, 0, 110))
        ov.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * K)))
    d.rounded_rectangle((mx * K, my * K, (mx + mw) * K, (my + mh) * K), R * K, fill=mbg, outline=line + (255,), width=K)
    # search
    d.rounded_rectangle(((mx + 14) * K, (my + 14) * K, (mx + mw - 14) * K, (my + 44) * K), (8 if doorway else 2) * K,
                        fill=(C['base'] if doorway else C['m_bg2']) + (255,), outline=(acc if doorway else line) + (255,), width=K)
    d.text(((mx + 26) * K, (my + 21) * K), 'Type to search…', fill=mut, font=font(11))
    cats = ['Favorites', 'Accessories', 'Graphics', 'Internet', 'Office', 'Programming', 'System Tools']
    apps = ['Firefox', 'Files', 'kitty', 'VS Code', 'System Monitor', 'Software Manager', 'Settings']
    for i, c in enumerate(cats):
        yy = my + 60 + i * 36
        if i == 3:
            d.rounded_rectangle(((mx + 10) * K, (yy - 4) * K, (mx + 130) * K, (yy + 26) * K), (6 if doorway else 0) * K, fill=hover + (255,))
            if doorway:
                d.rounded_rectangle(((mx + 10) * K, (yy + 2) * K, (mx + 13) * K, (yy + 20) * K), K, fill=acc + (255,))
        d.text(((mx + 20) * K, (yy + 3) * K), c, fill=txt if i == 3 else mut, font=font(11))
    for i, a in enumerate(apps):
        yy = my + 60 + i * 36
        if i == 0:
            d.rounded_rectangle(((mx + 140) * K, (yy - 4) * K, (mx + mw - 10) * K, (yy + 26) * K), (6 if doorway else 0) * K,
                                fill=(C['sel'] if doorway else C['m_acc']) + (255,))
        ic = '/usr/share/icons/Papirus/64x64/apps/' + ['firefox', 'nemo', 'kitty', 'code', 'utilities-system-monitor', 'mintinstall', 'preferences-desktop'][i] + '.svg'
        try:
            im = icon(ic, 20)
            ov.alpha_composite(im, ((mx + 150) * K, (yy + 1) * K))
        except Exception:
            pass
        d.text(((mx + 178) * K, (yy + 3) * K), a, fill=(C['bright'] if doorway else (255, 255, 255)) if i == 0 else txt, font=font(11))

    # calendar popup (center)
    cw, chh = 300, 330
    cx, cy = SW / 2 - cw / 2, PH + 8
    if doorway:
        sh = Image.new('RGBA', bg.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle(((cx + 2) * K, (cy + 6) * K, (cx + cw + 2) * K, (cy + chh + 6) * K), R * K, fill=(0, 0, 0, 110))
        ov.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10 * K)))
    d.rounded_rectangle((cx * K, cy * K, (cx + cw) * K, (cy + chh) * K), R * K, fill=mbg, outline=line + (255,), width=K)
    d.text(((cx + 18) * K, (cy + 14) * K), 'Tuesday', fill=txt, font=font(16, 'SemiBold'))
    d.text(((cx + 18) * K, (cy + 36) * K), '27 October 2026', fill=mut, font=font(11))
    d.text(((cx + cw / 2 - 40) * K, (cy + 64) * K), 'October 2026', fill=txt, font=font(11, 'SemiBold'))
    days = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
    gx, gw = cx + 18, (cw - 36) / 7
    for i, s in enumerate(days):
        d.text(((gx + i * gw + 9) * K, (cy + 88) * K), s, fill=mut, font=font(9.5))
    # Oct 2026 starts Thursday; lunar: Oct 10 2026 = 1/9 → day n lunar = n-9 (approx for mock)
    for n in range(1, 32):
        idx = n + 2
        r, c = idx // 7, idx % 7
        x0, y0 = gx + c * gw, cy + 108 + r * 36
        if n == 27:
            d.rounded_rectangle(((x0 + 3) * K, (y0 - 2) * K, (x0 + gw - 3) * K, (y0 + 32) * K), (8 if doorway else 2) * K, fill=acc + (255,))
        ln = n - 9 if n >= 10 else n + 21
        lt = '1/9' if ln == 1 else str(ln)
        fc = (C['base'] if doorway else (255, 255, 255)) if n == 27 else txt
        s = str(n)
        f1 = font(11, 'SemiBold' if n == 27 else 'Regular')
        d.text(((x0 + gw / 2) * K - d.textlength(s, font=f1) / 2, (y0 + 1) * K), s, fill=fc, font=f1)
        f2 = font(7.5)
        lc = fc if n == 27 else ((C['orange'] if ln == 1 else C['muted']) if doorway else (150, 150, 155))
        d.text(((x0 + gw / 2) * K - d.textlength(lt, font=f2) / 2, (y0 + 17) * K), lt, fill=lc, font=f2)
    d.text(((cx + 18) * K, (cy + chh - 24) * K), 'Lunar 18/9/2026  ·  year of the Horse', fill=mut, font=font(9.5))

    out = bg.copy()
    out.alpha_composite(ov)
    return out


top = Image.new('RGBA', (SW * K * 2 + 24 * K, SH * K + 50 * K), C['base'] + (255,))
dd = ImageDraw.Draw(top)
dd.text((12 * K, 14 * K), 'NOW  ·  Mint-Y-Dark-Aqua', fill=C['muted'], font=font(14, 'SemiBold'))
dd.text(((SW + 36) * K, 14 * K), 'DOORWAY SHELL  ·  translucent teal panel, rounded popups, orange accents', fill=C['orange'], font=font(14, 'SemiBold'))
top.alpha_composite(shell(False), (12 * K, 46 * K))
top.alpha_composite(shell(True), ((SW + 36) * K, 46 * K))
top = top.resize((top.width // 2 * 3 // 2 // 1, top.height // 2 * 3 // 2), Image.LANCZOS)
top.convert('RGB').save(OUT + 'shell.png')
print('ok')
