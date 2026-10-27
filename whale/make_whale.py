# Doorway rice — kitty greeting whale: a humpback drawn in a grid of small rounded squares
# (contribution-graph style), swimming in a seamless loop. Output is played by whale-greet
# with `kitten icat` beside fastfetch.
#   python3 -I ~/rice/whale/make_whale.py   ->  ~/.config/kitty/whale-grid.gif
# Sized for kitty cells of 20x44 px (GeistMono 12.5 at 2x) and an area of AREA_COLS x AREA_ROWS cells.
import math, random
from PIL import Image, ImageDraw

OUT = '/home/notrealqt/.config/kitty/whale-grid.gif'
CELL_W, CELL_H = 20, 44
AREA_COLS, AREA_ROWS = 36, 13
PITCH, SQ, RAD = 10, 8, 2                  # square pitch / size / corner radius (px)
W_PX, H_PX = AREA_COLS * CELL_W, AREA_ROWS * CELL_H
GW, GH = W_PX // PITCH, H_PX // PITCH      # 72 x 57 squares
FRAMES, MS = 48, 85                        # ~4 s loop

BG = (11, 29, 34)                          # kitty background (Doorway base)
TEAL = [(19, 44, 50), (26, 67, 75), (36, 93, 102), (51, 128, 139), (79, 154, 166), (134, 195, 203), (196, 230, 234)]
SPARK = [(169, 84, 17), (227, 146, 54), (245, 189, 102), (242, 229, 184)]

EMPTY, BACK, BELLY, FIN, FLUKE, EYE, GROOVE, MOUTH = range(8)


# ───────────── whale shape (units of body length L; head points right) ─────────────
def ttop(s):
    if s < 0.27: return 0.150 * (s / 0.27) ** 0.55
    return 0.150 * math.cos((s - 0.27) / 0.73 * math.pi / 2) ** 1.25 + 0.012


def tbot(s):
    if s < 0.30: return 0.128 * (s / 0.30) ** 0.48
    return 0.128 * math.cos((s - 0.30) / 0.70 * math.pi / 2) ** 1.7 + 0.012


def whale(W, H, ph):
    """region image at resolution W x H for swim phase ph (radians); also blowhole + head points"""
    im = Image.new('L', (W, H), EMPTY)
    d = ImageDraw.Draw(im)
    L = 0.64 * W
    x0, y0 = W * 0.86, H * 0.50 + 0.02 * L * math.sin(ph)
    tilt = 0.035 * math.sin(ph + 0.8)

    def P(s, v):
        return (x0 - L * s,
                y0 + L * (v + 0.018 * math.sin(math.pi * s) + 0.05 * s ** 2.5 * math.sin(ph - 3.0 * s) + tilt * (s - 0.4)))
    S = [i / 120 for i in range(121)]
    top = [P(s, -ttop(s)) for s in S]
    bot = [P(s, tbot(s)) for s in S]
    d.polygon(top + bot[::-1], fill=BACK)
    bs = [s for s in S if s < 0.66]
    d.polygon([P(s, tbot(s) * 0.12) for s in bs] + [P(s, tbot(s)) for s in bs[::-1]], fill=BELLY)
    gw = max(1, W // 160)
    for k in range(4):                                     # throat grooves
        f = 0.34 + 0.17 * k
        d.line([P(s, tbot(s) * f) for s in S if 0.04 < s < 0.40 - 0.035 * k], fill=GROOVE, width=gw)
    d.line([P(s, 0.012 + 0.08 * s) for s in S if s < 0.25], fill=MOUTH, width=gw)
    # flukes
    jx, jy = P(1.0, 0)
    ang = 0.42 * math.sin(ph - 3.0)

    def R(u, v):
        u, v = -u * L, v * L
        return (jx + u * math.cos(ang) - v * math.sin(ang), jy + u * math.sin(ang) + v * math.cos(ang))
    d.polygon([R(-0.01, -0.012), R(0.04, -0.05), R(0.10, -0.11), R(0.17, -0.16), R(0.15, -0.09), R(0.12, -0.03),
               R(0.10, 0.0), R(0.12, 0.03), R(0.15, 0.08), R(0.16, 0.13), R(0.09, 0.09), R(0.04, 0.045), R(-0.01, 0.012)],
              fill=FLUKE)
    # long white pectoral fin
    rx, ry = P(0.27, tbot(0.27) * 0.55)
    fa = math.radians(38 + 14 * math.sin(ph + 1.2))
    Lf = 0.30 * L
    ux, uy = -math.cos(fa), math.sin(fa)
    nx, ny = -uy, ux
    d.polygon([(rx + nx * 0.035 * L, ry + ny * 0.035 * L), (rx + ux * Lf * 0.5 + nx * 0.03 * L, ry + uy * Lf * 0.5 + ny * 0.03 * L),
               (rx + ux * Lf, ry + uy * Lf), (rx + ux * Lf * 0.5 - nx * 0.012 * L, ry + uy * Lf * 0.5 - ny * 0.012 * L),
               (rx - nx * 0.02 * L, ry - ny * 0.02 * L)], fill=FIN)
    d.polygon([P(0.60, -ttop(0.60) + 0.01), P(0.67, -ttop(0.67) - 0.035), P(0.68, -ttop(0.68) + 0.01)], fill=BACK)
    ex, ey = P(0.15, 0.022)
    r = L * 0.011
    d.ellipse((ex - r, ey - r, ex + r, ey + r), fill=EYE)
    # head tubercles (the bumps humpbacks have) + chin barnacles, as (x, y) points
    bumps = [P(s, -ttop(s) + 0.02) for s in (0.04, 0.07, 0.10)] + [P(s, tbot(s) - 0.012) for s in (0.05, 0.09)]
    return im, P(0.17, -ttop(0.17)), bumps


# ───────────── one frame → grid of (level, kind) ─────────────
K = 4                                                     # sub-samples per square side
rnd = random.Random(21)
WATER = [(rnd.randrange(GW), rnd.randrange(GH), rnd.random()) for _ in range(70)]
BUB = [(rnd.random(), rnd.random()) for _ in range(7)]
FISH = [(0.18, 0.80), (0.24, 0.84), (0.21, 0.88)]         # small school, offsets in grid fractions


def tail_y(ph):
    L = 0.64 * GW
    return GH * 0.50 + 0.02 * L * math.sin(ph) + L * 0.05 * math.sin(ph - 3.0)


def frame(t):
    ph = 2 * math.pi * ((2 * t) % 1.0)                    # two tail strokes per loop
    lv = [[0] * GW for _ in range(GH)]
    kind = [[None] * GW for _ in range(GH)]
    # water: quiet squares drifting left one full width per loop (seamless)
    for x, y, z in WATER:
        gx = int(x - t * GW) % GW
        lv[y][gx] = 1 if z < 0.85 else 2
    # light rays: slow diagonal band
    band = (t * (GW + GH)) % (GW + GH) - GH * 0.6
    for gy in range(GH):
        for gx in range(GW):
            if -1.5 < (gx + gy * 0.55) - band < 1.5:
                lv[gy][gx] = max(lv[gy][gx], 1)
    # little fish school crossing right→left once per loop, low in the water
    for fx, fy in FISH:
        gx = int((1.15 - t * 1.3 + fx - 0.18) * GW)
        gy = int(fy * GH + math.sin(t * 12 + fx * 30))
        for dx, l in ((0, 3), (1, 2), (2, 2), (3, 1)):
            if 0 <= gx + dx < GW and 0 <= gy < GH:
                lv[gy][gx + dx] = max(lv[gy][gx + dx], l)
    # whale
    mask, blow, bumps = whale(GW * K, GH * K, ph)
    m = mask.load()
    cols_top, cols_bot = {}, {}
    cells = {}
    for gy in range(GH):
        for gx in range(GW):
            cnt = {}
            for yy in range(gy * K, gy * K + K):
                for xx in range(gx * K, gx * K + K):
                    r = m[xx, yy]
                    cnt[r] = cnt.get(r, 0) + 1
            fg = sum(v for r, v in cnt.items() if r != EMPTY)
            if fg < K * K * 0.35:
                continue
            if cnt.get(EYE, 0) >= 2: reg = EYE
            elif cnt.get(MOUTH, 0) >= 2: reg = MOUTH
            elif cnt.get(GROOVE, 0) >= 2: reg = GROOVE
            else: reg = max((r for r in cnt if r != EMPTY), key=lambda r: cnt[r])
            cells[gx, gy] = reg
            if reg in (BACK, BELLY, GROOVE, MOUTH, EYE):
                cols_top[gx] = min(cols_top.get(gx, gy), gy)
                cols_bot[gx] = max(cols_bot.get(gx, gy), gy)
    for (gx, gy), reg in cells.items():
        top, bot = cols_top.get(gx, gy), cols_bot.get(gx, gy)
        rel = (gy - top) / max(1, bot - top)
        if reg == EYE:
            l = 0
        elif reg in (MOUTH, GROOVE):
            l = 3
        elif reg == BELLY:
            l = 5
        elif reg == FIN:
            l = 6 if (gx, gy - 1) in cells and cells[gx, gy - 1] == FIN else 5
        elif reg == FLUKE:
            l = 5 if ((gx - 1, gy) not in cells) else 4
        else:  # back: rim light on top, darker toward the flank
            l = 6 if gy == top else 5 if rel < 0.18 else 4 if rel < 0.5 else 3
        lv[gy][gx] = l
        kind[gy][gx] = 'whale'
    for bx, by in bumps:
        gx, gy = int(bx / K), int(by / K)
        if (gx, gy) in cells:
            lv[gy][gx] = 6
    # wake: past tail positions, spreading and fading as they drift left
    tail_x = GW * 0.86 - 0.64 * GW - 0.10 * 0.64 * GW
    for j in range(1, 20):
        tp = 2 * math.pi * ((2 * (t - j / FRAMES)) % 1.0)
        gx = int(round(tail_x - j * 0.9))
        for off in (-1, 0, 1):
            gy = int(round(tail_y(tp) + off * (1 + j * 0.15) + math.sin(j * 1.3)))
            if 0 <= gx < GW and 0 <= gy < GH and kind[gy][gx] is None and (off == 0 or j > 3):
                lv[gy][gx] = max(lv[gy][gx], 3 if j < 5 else 2 if j < 12 else 1)
    bx, by = blow[0] / K, blow[1] / K
    # bubbles from the mouth, brightening just before they pop
    for k, (o, w) in enumerate(BUB):
        tt = (t * 2 + o) % 1.0
        gx = int(GW * 0.86 + 1 + w * 4 + math.sin(tt * 9 + k)) % GW
        gy = int(GH * 0.55 - tt * GH * 0.6)
        if 0 <= gy < GH and kind[gy][gx] is None:
            lv[gy][gx] = 3 if tt < 0.75 else 6
    # spout once per loop: column up, then two arcs of spray falling
    if 0.55 <= t < 0.92:
        u = (t - 0.55) / 0.37
        h = 16 * math.sin(math.pi * min(1, u * 1.4))
        for i in range(int(h)):
            gy = int(by) - 1 - i
            for gx in (int(bx), int(bx) + (1 if i > h * 0.6 else 0)):
                if 0 <= gy < GH:
                    lv[gy][gx] = 3 if i > h - 2 else 2 if i > h - 5 else 1
                    kind[gy][gx] = 'spark'
        if u > 0.3:
            sp = (u - 0.3) / 0.7
            for side in (-1, 1):
                for k in range(6):
                    gx = int(bx + side * (1.5 + k * 0.7 + sp * 7))
                    gy = int(by - 16 + 1 + sp * sp * 16 + k * 0.8)
                    if 0 <= gx < GW and 0 <= gy < GH and kind[gy][gx] is None:
                        lv[gy][gx] = 2 if k < 3 else 1
                        kind[gy][gx] = 'spark'
    return lv, kind


def render(t):
    img = Image.new('RGB', (W_PX, H_PX), BG)
    d = ImageDraw.Draw(img)
    lv, kind = frame(t)
    ox = (W_PX - GW * PITCH) // 2
    oy = (H_PX - GH * PITCH) // 2
    for gy in range(GH):
        for gx in range(GW):
            l = lv[gy][gx]
            c = SPARK[min(3, l)] if kind[gy][gx] == 'spark' else TEAL[min(6, l)]
            x, y = ox + gx * PITCH, oy + gy * PITCH
            d.rounded_rectangle((x, y, x + SQ - 1, y + SQ - 1), RAD, fill=c)
    return img


if __name__ == '__main__':
    frames = [render(i / FRAMES) for i in range(FRAMES)]
    # fixed palette = exactly the colours used (frame 0 has no spout, so don't learn it from a frame)
    pal = Image.new('P', (1, 1))
    cols = [BG] + TEAL + SPARK
    pal.putpalette([v for c in cols for v in c] + [0] * (768 - 3 * len(cols)))
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    # palette index 0 = BG is transparent, so kitty's see-through background shows between the squares
    q[0].save(OUT, save_all=True, append_images=q[1:], duration=MS, loop=0, optimize=False, disposal=2, transparency=0)
    frames[FRAMES * 2 // 3].save('/home/notrealqt/rice/whale/frame.png')
    print(OUT, f'{GW}x{GH} squares, {W_PX}x{H_PX}px, {FRAMES} frames')
