# Doorway rice — mockups for #9 panel (+ card under it), #15 launcher, #10 lock screen, #8 cursor.
# python3 -I ~/rice/preview/make_round2_mock.py  ->  panel-v2.png launcher.png lock-v2.png cursor.png
import glob, struct, sys
import gi
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = '/home/notrealqt/rice/preview/'
FS = '/home/notrealqt/.local/share/fonts/'
WALL = Image.open('/home/notrealqt/Pictures/wallhaven-vp2l1m_1920x1080.png').convert('RGBA')
C = dict(base=(11, 29, 34), surface=(18, 41, 47), overlay=(29, 59, 66), line=(44, 74, 80), muted=(124, 145, 150),
         text=(232, 223, 198), bright=(242, 229, 184), teal=(79, 154, 166), sel=(46, 118, 130), orange=(227, 146, 54),
         amber=(215, 134, 21), olive=(154, 165, 86), red=(205, 92, 69), mauve=(179, 154, 171))
_fc = {}


def F(size, w='Regular', mono=False):
    key = (size, w, mono)
    if key not in _fc:
        pat = f'{FS}GeistMonoNF/GeistMonoNerdFont-{w}.otf' if mono else f'{FS}**/Geist-{w}.*tf'
        hits = sorted(glob.glob(pat, recursive=True)) or sorted(glob.glob(f'{FS}**/Geist*{w}*', recursive=True))
        _fc[key] = ImageFont.truetype(hits[0], int(size))
    return _fc[key]


def svg(path, size):
    try:
        pb = GdkPixbuf.Pixbuf.new_from_file_at_size(path, size, size)
    except Exception:
        return None
    if not pb.get_has_alpha():
        pb = pb.add_alpha(False, 0, 0, 0)
    return Image.frombytes('RGBA', (pb.get_width(), pb.get_height()), pb.get_pixels(), 'raw', 'RGBA', pb.get_rowstride())


P = '/usr/share/icons/Papirus-Dark/'
def app(n, s): return svg(f'{P}64x64/apps/{n}.svg', s)
def tray(n, s): return svg(f'{P}22x22/panel/{n}.svg', s)


def text(d, xy, s, c='text', f=None, anchor='la'):
    d.text(xy, s, fill=C[c] if isinstance(c, str) else c, font=f or F(22), anchor=anchor)


def shadow(img, box, r, blur=18, a=120):
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((box[0], box[1] + 8, box[2], box[3] + 8), r, fill=(0, 0, 0, a))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))


def sheet(title, panes, cols=2, pad=40, head=90, label_h=70):
    pw, ph = panes[0][2].size
    rows = (len(panes) + cols - 1) // cols
    W, H = pad + cols * (pw + pad), head + rows * (ph + label_h + pad)
    out = Image.new('RGBA', (W, H), C['base'] + (255,))
    d = ImageDraw.Draw(out)
    text(d, (pad, 30), title, 'bright', F(38, 'SemiBold'))
    for i, (key, name, im) in enumerate(panes):
        x, y = pad + (i % cols) * (pw + pad), head + (i // cols) * (ph + label_h + pad)
        text(d, (x, y + 8), key, 'orange', F(30, 'Bold'))
        text(d, (x + 44, y + 12), name, 'text', F(24))
        out.alpha_composite(im, (x, y + label_h))
        d.rounded_rectangle((x - 1, y + label_h - 1, x + pw, y + label_h + ph), 14, outline=C['line'], width=2)
    return out


# ═══════════════════════ #9 panel + card position ═══════════════════════
# drawn at the laptop's real framebuffer size (3072x1728 = 1536x864 logical at 2x), then shrunk
LW, LH, PH = 3072, 1728, 80
CARD = Image.open(OUT + 'card-real.png').convert('RGBA')


def desk():
    return WALL.resize((LW, LH)).copy()


def win_list(d, img, x, y, icons, active=1, s=44, gap=22, style='line'):
    for i, n in enumerate(icons):
        ic = app(n, s)
        cx = x + i * (s + gap)
        if i == active:
            if style == 'line':
                d.rounded_rectangle((cx - 10, y + PH - 10 - 4, cx + s + 10, y + PH - 10), 2, fill=C['orange'])
            else:
                d.ellipse((cx + s / 2 - 4, y + PH - 16, cx + s / 2 + 4, y + PH - 8), fill=C['orange'])
        elif i in (2, 3) and style != 'line':
            d.ellipse((cx + s / 2 - 3, y + PH - 15, cx + s / 2 + 3, y + PH - 9), fill=C['muted'])
        if ic:
            img.alpha_composite(ic, (cx, y + (PH - s) // 2))
    return x + len(icons) * (s + gap)


def stats(d, x, y, full, f=None):
    f = f or F(22, 'Regular', mono=True)
    parts = [('↓', 'muted'), ('1.2M ', 'text'), ('↑', 'muted'), ('84K', 'text'), ('  ·  ', 'line'),
             ('CPU ', 'muted'), ('54°', 'text'), ('  ·  ', 'line')]
    if full:
        parts += [('AMD ', 'muted'), ('48°', 'text'), ('  ·  ', 'line'), ('NVI ', 'muted'), ('zz', 'muted'), ('  ·  ', 'line'),
                  ('SSD ', 'muted'), ('16%', 'text'), ('  ·  ', 'line')]
    parts += [('BAT ', 'muted'), ('82%', 'olive')]
    for s, c in parts:
        d.text((x, y), s, fill=C[c], font=f, anchor='lm')
        x += d.textlength(s, font=f)
    return x


def width_of(d, full):
    tmp = Image.new('RGBA', (10, 10)); return stats(ImageDraw.Draw(tmp), 0, 0, full)


TRAY = ['network-wireless-signal-excellent', 'audio-volume-high', 'battery-080-charging']
APPS = ['nemo', 'firefox', 'kitty', 'google-chrome', 'code']


def panel(variant):
    img = desk()
    d = ImageDraw.Draw(img)
    y = 0
    if variant == 'bar':      # A: one clean full-width bar
        d.rectangle((0, 0, LW, PH), fill=C['base'] + (232,))
        d.line((0, PH, LW, PH), fill=C['line'], width=2)
        d.rounded_rectangle((16, 14, 68, 66), 12, fill=C['orange'])
        d.ellipse((28, 26, 56, 54), outline=C['base'], width=5)
        win_list(d, img, 104, 0, APPS, style='line')
        text(d, (LW / 2, PH / 2), 'Tue 27 Oct   17:52', 'bright', F(25, 'SemiBold'), 'mm')
        sx = LW - 40 - 3 * 50 - 30 - width_of(d, False)
        stats(d, sx, PH / 2, False)
        for i, n in enumerate(TRAY):
            ic = tray(n, 36)
            if ic: img.alpha_composite(ic, (LW - 40 - (3 - i) * 50, (PH - 36) // 2))
    else:                    # B / C: three floating islands on a clear bar
        full = variant == 'islands-full'
        m, ih = 10, PH - 20
        L = (14, m, 14 + 104 + len(APPS) * 66 + 10, m + ih)
        ctext = 'Tue 27 Oct   17:52'
        cw = d.textlength(ctext, font=F(25, 'SemiBold')) + 64
        Cb = (LW / 2 - cw / 2, m, LW / 2 + cw / 2, m + ih)
        rw = width_of(d, full) + 3 * 50 + 70
        R = (LW - 14 - rw, m, LW - 14, m + ih)
        for b in (L, Cb, R):
            shadow(img, b, ih / 2, 10, 90)
            d.rounded_rectangle(b, ih / 2, fill=C['base'] + (225,), outline=C['line'], width=2)
        d.ellipse((L[0] + 14, m + 10, L[0] + 14 + ih - 20, m + ih - 10), fill=C['orange'])
        d.ellipse((L[0] + 26, m + 22, L[0] + 2 + ih - 20, m + ih - 22), outline=C['base'], width=4)
        win_list(d, img, L[0] + 92, 0, APPS, style='dot')
        text(d, ((Cb[0] + Cb[2]) / 2, PH / 2), ctext, 'bright', F(25, 'SemiBold'), 'mm')
        x = stats(d, R[0] + 30, PH / 2, full)
        for i, n in enumerate(TRAY):
            ic = tray(n, 34)
            if ic: img.alpha_composite(ic, (int(x + 20 + i * 50), (PH - 34) // 2))
    # the conky card, always on the panel's screen, right side, just under the panel
    img.alpha_composite(CARD, (LW - CARD.width - 24, PH + 24))
    return img.resize((LW // 2, LH // 2), Image.LANCZOS)


panes = [('A', 'Clean bar — one solid strip, small stats, only wifi · sound · battery', panel('bar')),
         ('B', 'Islands — floating pills, small stats (↓↑ · CPU · BAT)', panel('islands')),
         ('C', 'Islands + full stats (↓↑ · CPU · AMD · NVI · SSD · BAT)', panel('islands-full'))]


def two_screens():
    # diagram: where things live with 2 monitors
    W, H = 1536, 864
    img = Image.new('RGBA', (W, H), C['surface'] + (255,))
    d = ImageDraw.Draw(img)
    lap = (90, 300, 90 + 560, 300 + 315)
    vs = (720, 200, 720 + 740, 200 + 416)
    for b, name in ((lap, 'laptop (eDP)'), (vs, 'ViewSonic')):
        im = WALL.resize((int(b[2] - b[0]), int(b[3] - b[1])))
        img.alpha_composite(im, (int(b[0]), int(b[1])))
        d.rectangle(b, outline=C['line'], width=3)
        text(d, ((b[0] + b[2]) / 2, b[3] + 34), name, 'muted', F(26), 'mm')
    d.rectangle((lap[0], lap[1], lap[2], lap[1] + 16), fill=C['base'])
    d.rounded_rectangle((lap[2] - 128, lap[1] + 24, lap[2] - 10, lap[1] + 24 + 190), 8, fill=C['base'] + (230,), outline=C['orange'], width=3)
    text(d, (lap[2] - 69, lap[1] + 120), 'card', 'orange', F(22, 'SemiBold'), 'mm')
    text(d, (lap[0], lap[1] - 60), 'panel + card always together', 'bright', F(30, 'SemiBold'))
    text(d, (lap[0], lap[1] - 24), 'on the laptop · card top-right under the panel', 'muted', F(22))
    text(d, ((vs[0] + vs[2]) / 2, vs[1] - 30), 'clean — just windows', 'muted', F(24), 'mm')
    text(d, (W / 2, 780), 'unplug the ViewSonic → nothing moves; plug it in → nothing moves', 'teal', F(26), 'mm')
    return img


panes.append(('', 'With 2 monitors (applies to A, B or C)', two_screens()))
sheet('#9 Panel — pick A, B or C  (40 px height kept)', panes).convert('RGB').save(OUT + 'panel-v2.png')

# ═══════════════════════ #15 launcher ═══════════════════════
LCH = [('firefox', 'Firefox', 'Web browser'), ('kitty', 'kitty', 'Terminal'), ('code', 'Visual Studio Code', 'Code editor'),
       ('nemo', 'Files', 'Browse the file system'), ('btop', 'btop', 'System monitor'), ('wireshark', 'Wireshark', 'Network analyzer')]


def launcher(style):
    img = WALL.resize((1536, 864))
    img = Image.alpha_composite(img, Image.new('RGBA', img.size, (0, 0, 0, 70)))
    d = ImageDraw.Draw(img)
    if style == 'spot':
        w, x0, y0 = 640, 448, 190
        h = 76 + len(LCH) * 62 + 24
        shadow(img, (x0, y0, x0 + w, y0 + h), 18, 24, 140)
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 18, fill=C['surface'] + (245,), outline=C['line'], width=2)
        d.text((x0 + 28, y0 + 38), '', fill=C['orange'], font=F(26, 'Regular', mono=True), anchor='lm')
        d.text((x0 + 66, y0 + 38), 'fi', fill=C['bright'], font=F(26), anchor='lm')
        d.line((x0 + 66 + d.textlength('fi', font=F(26)) + 3, y0 + 22, x0 + 66 + d.textlength('fi', font=F(26)) + 3, y0 + 54), fill=C['orange'], width=2)
        d.text((x0 + w - 26, y0 + 38), 'apps · run · files', fill=C['muted'], font=F(17), anchor='rm')
        d.line((x0, y0 + 76, x0 + w, y0 + 76), fill=C['line'], width=2)
        for i, (ic, n, desc) in enumerate(LCH):
            yy = y0 + 88 + i * 62
            if i == 0:
                d.rounded_rectangle((x0 + 12, yy, x0 + w - 12, yy + 56), 10, fill=C['sel'])
                d.rounded_rectangle((x0 + 12, yy + 14, x0 + 16, yy + 42), 2, fill=C['orange'])
            im = app(ic, 36)
            if im: img.alpha_composite(im, (x0 + 30, yy + 10))
            d.text((x0 + 82, yy + 28), n, fill=C['bright'] if i == 0 else C['text'], font=F(21, 'Medium' if i == 0 else 'Regular'), anchor='lm')
            d.text((x0 + w - 28, yy + 28), desc, fill=C['text'] if i == 0 else C['muted'], font=F(16), anchor='rm')
    else:  # grid
        w, h, x0, y0 = 900, 560, 318, 150
        shadow(img, (x0, y0, x0 + w, y0 + h), 22, 24, 140)
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 22, fill=C['surface'] + (240,), outline=C['line'], width=2)
        d.rounded_rectangle((x0 + 220, y0 + 30, x0 + w - 220, y0 + 82), 26, fill=C['base'], outline=C['orange'], width=2)
        d.text((x0 + w / 2, y0 + 56), 'Search apps…', fill=C['muted'], font=F(20), anchor='mm')
        names = ['firefox', 'kitty', 'code', 'nemo', 'btop', 'wireshark', 'google-chrome', 'org.gnome.Calculator',
                 'gimp', 'vlc', 'preferences-desktop', 'mintinstall']
        labels = ['Firefox', 'kitty', 'VS Code', 'Files', 'btop', 'Wireshark', 'Chrome', 'Calculator', 'GIMP', 'VLC', 'Settings', 'Software']
        for i, (n, lab) in enumerate(zip(names, labels)):
            cx, cy = x0 + 90 + (i % 6) * 144, y0 + 130 + (i // 6) * 190
            if i == 0:
                d.rounded_rectangle((cx - 20, cy - 14, cx + 108, cy + 136), 16, fill=C['overlay'], outline=C['orange'], width=2)
            im = app(n, 88)
            if im: img.alpha_composite(im, (cx, cy))
            d.text((cx + 44, cy + 112), lab, fill=C['text'], font=F(18), anchor='mm')
    return img


def menu_only():
    img = WALL.resize((1536, 864))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1536, 40), fill=C['base'] + (232,))
    d.rounded_rectangle((8, 7, 34, 33), 6, fill=C['orange'])
    x0, y0, w, h = 8, 48, 520, 600
    shadow(img, (x0, y0, x0 + w, y0 + h), 10, 16, 110)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 10, fill=C['surface'], outline=C['line'], width=2)
    d.rounded_rectangle((x0 + 16, y0 + 16, x0 + w - 16, y0 + 58), 8, fill=C['base'], outline=C['orange'], width=2)
    d.text((x0 + 32, y0 + 37), 'Type to search…', fill=C['muted'], font=F(18), anchor='lm')
    for i, c in enumerate(['Favorites', 'Accessories', 'Graphics', 'Internet', 'Office', 'Programming', 'Sound & Video', 'System Tools']):
        d.text((x0 + 30, y0 + 100 + i * 56), c, fill=C['muted'], font=F(18), anchor='lm')
    for i, (ic, n, _) in enumerate(LCH):
        yy = y0 + 76 + i * 56
        im = app(ic, 30)
        if im: img.alpha_composite(im, (x0 + 210, yy + 9))
        d.text((x0 + 254, yy + 24), n, fill=C['text'], font=F(18), anchor='lm')
    d.text((1000, 400), 'nothing new to install —\nthe themed Cinnamon menu\nyou already have (Super key)', fill=C['bright'], font=F(26), anchor='mm', align='center')
    return img


sheet('#15 App launcher — opens with Super+Space (A/B) or Super (C)', [
    ('A', 'Rofi · spotlight — type, Enter. Also runs commands & finds files', launcher('spot')),
    ('B', 'Rofi · grid — big icons, like a phone home screen', launcher('grid')),
    ('C', 'Keep the Cinnamon menu only', menu_only()),
]).convert('RGB').save(OUT + 'launcher.png')

# ═══════════════════════ #10 lock screen ═══════════════════════
def lock(clockfont, dim):
    W, H = 1536, 864
    img = WALL.resize((W, H))
    if dim:
        img = Image.alpha_composite(img, Image.new('RGBA', img.size, C['base'] + (110,)))
    d = ImageDraw.Draw(img)
    f = clockfont
    d.text((W / 2, 300), '17:52', fill=C['bright'], font=f, anchor='mm')
    d.text((W / 2, 400), 'Tuesday, 27 October', fill=C['text'], font=F(30, 'Light'), anchor='mm')
    box = (W / 2 - 220, 480, W / 2 + 220, 536)
    d.rounded_rectangle(box, 28, fill=C['base'] + (215,), outline=C['teal'], width=2)
    d.text((W / 2, 508), 'Password', fill=C['muted'], font=F(20), anchor='mm')
    d.text((W / 2, 566), 'notrealqt', fill=C['orange'], font=F(20, 'Medium'), anchor='mm')
    d.text((W - 30, 28), 'BAT 82%   ·   wifi', fill=C['text'], font=F(17), anchor='ra')
    return img


sheet('#10 Lock screen — fixed in the centre (no floating clock)', [
    ('A', 'Geist Thin clock · wallpaper dimmed teal', lock(F(150, 'Thin'), True)),
    ('B', 'GeistMono clock · wallpaper dimmed teal', lock(F(130, 'Light', mono=True), True)),
    ('C', 'Geist Thin clock · wallpaper as is', lock(F(150, 'Thin'), False)),
]).convert('RGB').save(OUT + 'lock-v2.png')

# ═══════════════════════ #8 cursor ═══════════════════════
def xcursor(path, want=48):
    b = open(path, 'rb').read()
    _, hsz, _, ntoc = struct.unpack_from('<4sIII', b, 0)
    best = None
    for i in range(ntoc):
        typ, sub, pos = struct.unpack_from('<III', b, 16 + i * 12)
        if typ == 0xfffd0002 and (best is None or abs(sub - want) < abs(best[0] - want)):
            best = (sub, pos)
    _, _, _, _, w, h, _, _, _ = struct.unpack_from('<IIIIIIIII', b, best[1])
    px = b[best[1] + 36: best[1] + 36 + w * h * 4]
    im = Image.frombytes('RGBA', (w, h), px, 'raw', 'BGRA')
    # Xcursor pixels are premultiplied; undo for PIL
    r, g, bb, a = im.split()
    return Image.merge('RGBA', (r, g, bb, a))


CUR = [('Bibata-Modern-Classic (now)', '/usr/share/icons/Bibata-Modern-Classic'),
       ('Bibata-Modern-Amber', '/tmp/claude-1000/-home-notrealqt/42c33590-5ba3-4402-898c-2ea10419bc51/scratchpad/dl-bibata/Bibata-Modern-Amber'),
       ('Bibata-Modern-Ice', '/usr/share/icons/Bibata-Modern-Ice'),
       ('XCursor-Pro-Dark', '/usr/share/icons/XCursor-Pro-Dark')]
SHAPES = [('left_ptr', 'pointer'), ('hand2', 'link'), ('xterm', 'text'), ('watch', 'busy'), ('fleur', 'move')]
cw, chh = 1536, 330
panes = []
for i, (name, path) in enumerate(CUR):
    img = WALL.crop((300, 200 + i * 150, 1700, 200 + i * 150 + 300)).resize((cw, chh))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((60, 60, cw - 60, chh - 60), 18, fill=C['surface'] + (225,), outline=C['line'], width=2)
    for j, (sh, lab) in enumerate(SHAPES):
        p = f'{path}/cursors/{sh}'
        try:
            im = xcursor(p, 96).resize((96, 96), Image.LANCZOS)
            img.alpha_composite(im, (150 + j * 270, 90))
        except Exception:
            pass
        d.text((198 + j * 270, 226), lab, fill=C['muted'], font=F(20), anchor='mm')
    panes.append((chr(65 + i), name, img))
sheet('#8 Cursor — pick one', panes).convert('RGB').save(OUT + 'cursor.png')
print('ok')
