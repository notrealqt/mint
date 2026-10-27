# Doorway rice — mockups for a new, more detailed swimming whale for the kitty greeting.
# One procedural humpback (body undulates, flukes flap, long pectoral fin, throat grooves),
# rendered four ways inside a 70x20-cell kitty window next to the fastfetch info.
# python3 -I ~/rice/preview/make_whale_mock.py  ->  whale-styles.png + whale-styles.gif
import math, random
from PIL import Image, ImageDraw, ImageFont

OUT = '/home/notrealqt/rice/preview/'
MONO = '/home/notrealqt/.local/share/fonts/GeistMonoNF/GeistMonoNerdFont-'
C = dict(base=(11, 29, 34), surface=(18, 41, 47), line=(44, 74, 80), muted=(124, 145, 150), text=(232, 223, 198),
         bright=(242, 229, 184), teal=(79, 154, 166), deep=(13, 94, 108), sel=(46, 118, 130), orange=(227, 146, 54),
         amber=(215, 134, 21), mauve=(179, 154, 171), olive=(154, 165, 86), red=(205, 92, 69), blue=(108, 159, 192))

COLS, ROWS = 70, 20            # kitty window in cells
WC, WR = 38, 14                # whale area (cells) — left of the info
CW, CH = 11, 23                # cell size in px for the mock

# region ids in the mask
BG, BACK, BELLY, FIN, FLUKE, EYE, GROOVE, EDGE = range(8)


# ───────────────────────── the whale ─────────────────────────
def whale_mask(W, H, t, polys=False):
    """Region map of the whale at animation phase t in [0,1). Head points right.
    Shape is defined in units of the body length L, so it never squashes."""
    im = Image.new('L', (W, H), BG)
    d = ImageDraw.Draw(im)
    ph = 2 * math.pi * t
    L = 0.80 * W
    x0, y0 = W * 0.90, H * 0.47 + 0.02 * L * math.sin(ph)
    tilt = 0.035 * math.sin(ph + 0.8)
    def P(s, v):                      # s: 0 nose .. 1 tail joint, v: offset in body lengths (down +)
        x = x0 - L * s
        y = y0 + L * (v + 0.018 * math.sin(math.pi * s) + 0.05 * s ** 2.5 * math.sin(ph - 3.0 * s) + tilt * (s - 0.4))
        return (x, y)
    def ttop(s):
        if s < 0.27: return 0.150 * (s / 0.27) ** 0.55
        return 0.150 * math.cos((s - 0.27) / 0.73 * math.pi / 2) ** 1.25 + 0.012
    def tbot(s):
        if s < 0.30: return 0.128 * (s / 0.30) ** 0.48
        return 0.128 * math.cos((s - 0.30) / 0.70 * math.pi / 2) ** 1.7 + 0.012
    N = 90
    S = [i / N for i in range(N + 1)]
    top = [P(s, -ttop(s)) for s in S]
    bot = [P(s, tbot(s)) for s in S]
    body = top + bot[::-1]
    d.polygon(body, fill=BACK)
    # pale belly / throat
    bs = [s for s in S if s < 0.66]
    d.polygon([P(s, tbot(s) * 0.15) for s in bs] + [P(s, tbot(s)) for s in bs[::-1]], fill=BELLY)
    # throat grooves + mouth line
    for k in range(3):
        f = 0.40 + 0.20 * k
        d.line([P(s, tbot(s) * f) for s in S if 0.04 < s < 0.36 - 0.04 * k], fill=GROOVE, width=max(1, W // 300))
    d.line([P(s, 0.012 + 0.08 * s) for s in S if s < 0.24], fill=EDGE, width=max(1, W // 260))
    # flukes: big, flapping round the tail joint
    jx, jy = P(1.0, 0)
    ang = 0.42 * math.sin(ph - 3.0)
    def R(u, v):
        u, v = -u * L, v * L
        return (jx + u * math.cos(ang) - v * math.sin(ang), jy + u * math.sin(ang) + v * math.cos(ang))
    fl = [R(-0.01, -0.012), R(0.04, -0.05), R(0.10, -0.11), R(0.17, -0.16), R(0.15, -0.09), R(0.12, -0.03),
          R(0.10, 0.0), R(0.12, 0.03), R(0.15, 0.08), R(0.16, 0.13), R(0.09, 0.09), R(0.04, 0.045), R(-0.01, 0.012)]
    d.polygon(fl, fill=FLUKE)
    # long white humpback pectoral fin
    rx, ry = P(0.27, tbot(0.27) * 0.55)
    fa = math.radians(38 + 14 * math.sin(ph + 1.2))
    Lf = 0.30 * L
    ux, uy = -math.cos(fa), math.sin(fa)
    nx, ny = -uy, ux
    fin = [(rx + nx * 0.035 * L, ry + ny * 0.035 * L),
           (rx + ux * Lf * 0.5 + nx * 0.03 * L, ry + uy * Lf * 0.5 + ny * 0.03 * L),
           (rx + ux * Lf, ry + uy * Lf),
           (rx + ux * Lf * 0.5 - nx * 0.012 * L, ry + uy * Lf * 0.5 - ny * 0.012 * L),
           (rx - nx * 0.02 * L, ry - ny * 0.02 * L)]
    d.polygon(fin, fill=FIN)
    # small dorsal fin
    d.polygon([P(0.60, -ttop(0.60) + 0.01), P(0.67, -ttop(0.67) - 0.035), P(0.68, -ttop(0.68) + 0.01)], fill=BACK)
    # outline + eye
    w = max(1, W // 220)
    d.line(body + [body[0]], fill=EDGE, width=w)
    d.line(fl + [fl[0]], fill=EDGE, width=w)
    ex, ey = P(0.15, 0.022)
    r = max(1.5, L * 0.010)
    d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=EYE)
    blow = P(0.17, -ttop(0.17))
    if polys:
        return im, blow, [body[::3], fl, fin]
    return im, blow


def particles(n, seed):
    rnd = random.Random(seed)
    return [(rnd.random(), rnd.random(), rnd.random()) for _ in range(n)]


DUST = particles(70, 3)


def bubbles(t, blow, W, H):
    out = []
    for k in range(5):
        tt = (t * 1.0 + k / 5) % 1.0
        out.append((blow[0] / W + 0.01 * math.sin(6 * tt + k), blow[1] / H - tt * 0.45, 1 - tt))
    return out


# ───────────────────────── renderers ─────────────────────────
COL = {BACK: C['teal'], BELLY: C['text'], FIN: C['teal'], FLUKE: C['teal'], GROOVE: C['muted'], EDGE: C['bright'], EYE: C['base']}
DENS = {BACK: 0.55, BELLY: 0.32, FIN: 0.6, FLUKE: 0.6, GROOVE: 0.9, EDGE: 1.0, EYE: 0.0}
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def lerp(a, b, f): return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


def shade(reg, yfrac):
    """colour with a little light-from-above on the back"""
    c = COL.get(reg, C['text'])
    if reg in (BACK, FIN, FLUKE):
        c = lerp(lerp(C['teal'], C['bright'], 0.25), C['deep'], min(1, max(0, yfrac)))
    return c


def r_braille(img, ox, oy, t):
    d = ImageDraw.Draw(img)
    W, H = WC * 2, WR * 4
    mask, blow = whale_mask(W * 4, H * 4, t)
    m = mask.resize((W, H), Image.NEAREST).load()
    # drifting plankton / water dots behind
    for i, (px, py, z) in enumerate(DUST[:45]):
        x = ((px - t * (0.25 + 0.5 * z)) % 1.0) * W
        y = py * H
        cx, cy = ox + int(x) // 2 * CW + (int(x) % 2) * CW / 2 + CW / 4, oy + int(y) // 4 * CH + (int(y) % 4) * CH / 4 + CH / 8
        d.ellipse((cx - 1.2, cy - 1.2, cx + 1.2, cy + 1.2), fill=lerp(C['base'], C['muted'] if z < 0.8 else C['orange'], 0.35 + 0.4 * z))
    for gy in range(H):
        for gx in range(W):
            reg = m[gx, gy]
            if reg == BG:
                continue
            dens = DENS[reg]
            if reg in (BACK, FIN, FLUKE):
                dens = 0.75 - 0.45 * (gy / H)
            if dens * 16 > BAYER[gy % 4][gx % 4]:
                cx = ox + gx // 2 * CW + (gx % 2) * CW / 2 + CW / 4
                cy = oy + gy // 4 * CH + (gy % 4) * CH / 4 + CH / 8
                c = shade(reg, gy / H * 1.4 - 0.2)
                rr = 1.7
                d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=c)
    for bx, by, a in bubbles(t, blow, W * 4, H * 4):
        cx, cy = ox + bx * WC * CW, oy + by * WR * CH
        if cy > oy:
            d.ellipse((cx - 2.4, cy - 2.4, cx + 2.4, cy + 2.4), outline=lerp(C['base'], C['bright'], a), width=1)


def r_halftone(img, ox, oy, t):
    d = ImageDraw.Draw(img)
    Wp, Hp = WC * CW, WR * CH
    mask, blow = whale_mask(Wp, Hp, t)
    m = mask.load()
    step = 7
    for i, (px, py, z) in enumerate(DUST):
        x = ((px - t * (0.2 + 0.6 * z)) % 1.0) * Wp
        r = 0.6 + 1.6 * z
        d.ellipse((ox + x - r, oy + py * Hp - r, ox + x + r, oy + py * Hp + r), fill=lerp(C['base'], C['orange'] if i % 7 == 0 else C['teal'], 0.25 + 0.5 * z))
    for gy in range(0, Hp, step):
        for gx in range(0, Wp, step):
            reg = m[gx, gy]
            if reg == BG:
                continue
            yfrac = gy / Hp * 1.5 - 0.25
            if reg in (BACK, FIN, FLUKE):
                rad = 2.0 + 1.6 * (1 - min(1, max(0, yfrac)))
            elif reg == BELLY:
                rad = 2.6
            elif reg == EDGE:
                rad = 3.4
            elif reg == EYE:
                continue
            else:
                rad = 1.6
            c = shade(reg, yfrac)
            off = (step / 2) if (gy // step) % 2 else 0
            d.ellipse((ox + gx + off - rad, oy + gy - rad, ox + gx + off + rad, oy + gy + rad), fill=c)
    for bx, by, a in bubbles(t, blow, Wp, Hp):
        cx, cy = ox + bx * Wp, oy + by * Hp
        if cy > oy:
            d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), outline=lerp(C['base'], C['bright'], a), width=1)


def r_pixels(img, ox, oy, t):
    d = ImageDraw.Draw(img)
    W, H = WC, WR * 2                       # half-block pixels
    mask, blow = whale_mask(W * 6, H * 6, t)
    m = mask.resize((W, H), Image.NEAREST).load()
    ph = CH / 2
    for i, (px, py, z) in enumerate(DUST[:25]):
        x = int(((px - t * (0.2 + 0.5 * z)) % 1.0) * W)
        y = int(py * H)
        if (x + y) % 3 == 0:
            d.rectangle((ox + x * CW, oy + y * ph, ox + x * CW + CW - 1, oy + y * ph + ph - 1), fill=lerp(C['base'], C['deep'], 0.6 + 0.4 * z))
    for gy in range(H):
        for gx in range(W):
            reg = m[gx, gy]
            if reg == BG:
                continue
            c = shade(reg, gy / H * 1.5 - 0.25)
            if reg == EDGE:
                c = C['bright'] if gy < H * 0.55 else C['muted']
            d.rectangle((ox + gx * CW, oy + gy * ph, ox + gx * CW + CW - 1, oy + gy * ph + ph - 1), fill=c)
    for bx, by, a in bubbles(t, blow, W * 6, H * 6):
        x, y = int(bx * W), int(by * H)
        if y >= 0:
            d.rectangle((ox + x * CW + 3, oy + y * ph + 2, ox + x * CW + CW - 4, oy + y * ph + ph - 2), outline=lerp(C['base'], C['bright'], a))


STARS = particles(60, 9)


def r_constellation(img, ox, oy, t):
    d = ImageDraw.Draw(img, 'RGBA')
    Wp, Hp = WC * CW, WR * CH
    mask, blow = whale_mask(Wp, Hp, t)
    m = mask.load()
    for i, (px, py, z) in enumerate(STARS):
        x = ((px - t * 0.08) % 1.0) * Wp
        tw = 0.5 + 0.5 * math.sin(2 * math.pi * (t * 2 + z * 5))
        r = 0.7 + 1.1 * z * tw
        d.ellipse((ox + x - r, oy + py * Hp - r, ox + x + r, oy + py * Hp + r), fill=C['muted'] + (int(90 + 120 * tw * z),))
    mask, blow, polys = whale_mask(Wp, Hp, t, polys=True)
    m = mask.load()
    step = 9
    for gy in range(0, Hp, step):
        for gx in range(0, Wp, step):
            reg = m[gx, gy]
            if reg in (BACK, FLUKE):
                d.ellipse((ox + gx - 1, oy + gy - 1, ox + gx + 1, oy + gy + 1), fill=C['teal'] + (110,))
            elif reg in (BELLY, FIN):
                d.ellipse((ox + gx - 1, oy + gy - 1, ox + gx + 1, oy + gy + 1), fill=C['text'] + (90,))
    k = 0
    for poly in polys:
        pts = poly[::2] if len(poly) > 40 else poly
        d.line([(ox + x, oy + y) for x, y in pts] + [(ox + pts[0][0], oy + pts[0][1])], fill=C['teal'] + (170,), width=1)
        for x, y in pts:
            k += 1
            r = 2.0 if k % 4 else 3.2
            col = C['orange'] if k % 11 == 0 else C['bright']
            d.ellipse((ox + x - r, oy + y - r, ox + x + r, oy + y + r), fill=col + (255,))
    # eye + fin + fluke hints
    for gy in range(0, Hp, 3):
        for gx in range(0, Wp, 3):
            if m[gx, gy] == EYE:
                d.ellipse((ox + gx - 2, oy + gy - 2, ox + gx + 2, oy + gy + 2), fill=C['orange'] + (255,))


# ───────────────────────── kitty window ─────────────────────────
FF = [('󰣭', 'Linux Mint 22.3'), ('', 'Linux 7.0.0-38'), ('󰧨', 'Cinnamon 6.6.9'), ('', 'kitty 0.49.2'),
      ('', 'Ryzen 7 4800H'), ('', '7.3 / 15.0 GiB'), ('󰅐', '5 hours, 6 mins')]


def kitty(render, t, title):
    W, H = COLS * CW + 40, ROWS * CH + 40
    img = Image.new('RGB', (W, H), C['base'])
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(MONO + 'Regular.otf', 17)
    fb = ImageFont.truetype(MONO + 'Bold.otf', 17)
    ox, oy = 20, 20
    render(img, ox, oy + CH, t)
    ix = ox + (WC + 3) * CW
    iy0 = 1
    d.text((ix, oy + CH * 2), 'notrealqt', fill=C['amber'], font=fb)
    d.text((ix + 9.5 * CW, oy + CH * 2), '@ doorway', fill=C['muted'], font=f)
    d.line((ix, oy + CH * 3 + 4, ix + 26 * CW, oy + CH * 3 + 4), fill=C['line'])
    for i, (k, v) in enumerate(FF):
        d.text((ix, oy + CH * (4 + i)), k, fill=C['teal'], font=f)
        d.text((ix + 3 * CW, oy + CH * (4 + i)), v, fill=C['text'], font=f)
    for i, c in enumerate(['line', 'red', 'olive', 'amber', 'blue', 'mauve', 'teal', 'text']):
        d.ellipse((ix + i * 2.2 * CW, oy + CH * 11.5, ix + i * 2.2 * CW + 14, oy + CH * 11.5 + 14), fill=C[c])
    d.text((ox, oy + CH * (WR + 3)), '~', fill=C['teal'], font=fb)
    d.text((ox, oy + CH * (WR + 4)), '❯', fill=C['orange'], font=fb)
    d.rectangle((ox + 2 * CW, oy + CH * (WR + 4) + 3, ox + 3 * CW - 2, oy + CH * (WR + 5) - 3), fill=C['text'])
    d.rectangle((0, 0, W - 1, H - 1), outline=C['line'], width=2)
    return img


STYLES = [('A', 'Braille dots — 2×4 dots per cell, fine detail, plankton drifting by', r_braille),
          ('B', 'Halftone — dot size = light, like a print; teal + orange specks', r_halftone),
          ('C', 'Pixel art — chunky half-block pixels, bubbles from the blowhole', r_pixels),
          ('D', 'Constellation — whale drawn by stars and faint lines, twinkling', r_constellation)]


def sheet(t, label=True):
    tiles = [kitty(fn, t, name) for key, name, fn in STYLES]
    tw, th = tiles[0].size
    pad, head = 24, 54
    out = Image.new('RGB', (pad + 2 * (tw + pad), head + 2 * (th + 44 + pad)), C['base'])
    d = ImageDraw.Draw(out)
    fg = ImageFont.truetype('/home/notrealqt/.local/share/fonts/Geist/' + 'Geist-SemiBold.ttf', 26) if False else ImageFont.truetype(MONO + 'Bold.otf', 22)
    fs = ImageFont.truetype(MONO + 'Regular.otf', 15)
    d.text((pad, 16), 'kitty greeting — new whale, 70×20 window. Pick A, B, C or D', fill=C['bright'], font=fg)
    for i, ((key, name, fn), tile) in enumerate(zip(STYLES, tiles)):
        x, y = pad + (i % 2) * (tw + pad), head + (i // 2) * (th + 44 + pad)
        d.text((x, y + 10), key, fill=C['orange'], font=fg)
        d.text((x + 30, y + 13), name, fill=C['text'], font=fs)
        out.paste(tile, (x, y + 44))
    return out


if __name__ == '__main__':
    sheet(0.15).save(OUT + 'whale-styles.png')
    frames = [sheet(i / 16) for i in range(16)]
    small = [f.resize((f.width * 2 // 3, f.height * 2 // 3), Image.LANCZOS).convert('P', palette=Image.ADAPTIVE, colors=128) for f in frames]
    small[0].save(OUT + 'whale-styles.gif', save_all=True, append_images=small[1:], duration=110, loop=0, optimize=True)
    print('ok')
