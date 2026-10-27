# Doorway rice — round 2 of whale mocks: GitHub-contribution-graph grids + more pixel-art takes.
# python3 -I ~/rice/preview/make_whale_mock2.py  ->  whale-styles2.png + whale-styles2.gif
import random
src = open('/home/notrealqt/rice/preview/make_whale_mock.py').read().split("if __name__ == '__main__':")[0]
exec(src)

GW, GH = WC, WR * 2            # one square per half-cell → 38 x 28 squares (squares are square)


def hexc(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


RAMP_TEAL = [hexc(h) for h in ('#132c32', '#1b4a52', '#2a6f79', '#4f9aa6', '#9fd0d6')]
RAMP_ORANGE = [hexc(h) for h in ('#132c32', '#5b3a19', '#94591a', '#d78615', '#f5bd66')]
RAMP_CREAM = [hexc(h) for h in ('#132c32', '#4d4a3f', '#8d8774', '#cfc6aa', '#f2e5b8')]


def sample(t, W=GW, H=GH, k=8):
    """per square: (region, coverage) from a k-times finer mask"""
    mask, blow = whale_mask(W * k, H * k, t)
    m = mask.load()
    grid = []
    for gy in range(H):
        row = []
        for gx in range(W):
            counts = {}
            for yy in range(gy * k, gy * k + k, 2):
                for xx in range(gx * k, gx * k + k, 2):
                    r = m[xx, yy]
                    counts[r] = counts.get(r, 0) + 1
            tot = sum(counts.values())
            fg = {r: c for r, c in counts.items() if r != BG}
            if not fg:
                row.append((BG, 0.0))
            else:
                reg = max(fg, key=fg.get)
                if EYE in fg and fg[EYE] >= 2: reg = EYE
                row.append((reg, sum(fg.values()) / tot))
        grid.append(row)
    return grid, (blow[0] / (W * k), blow[1] / (H * k))


def level(reg, cov, gy):
    if reg == BG or cov < 0.3:
        return 0
    if reg == EYE:
        return 0
    if reg == EDGE:
        return 4
    yfrac = gy / GH
    if reg in (BACK, FLUKE):
        lv = 3 if yfrac < 0.47 else 2
    elif reg in (BELLY, FIN):
        lv = 1
    elif reg == GROOVE:
        lv = 2
    else:
        lv = 2
    return lv if cov > 0.65 else max(1, lv - 1)


NOISE = random.Random(11)
NOISE_CELLS = [(NOISE.randrange(GW), NOISE.randrange(GH), NOISE.random()) for _ in range(40)]


def r_github(img, ox, oy, t, mode):
    d = ImageDraw.Draw(img)
    grid, blow = sample(t)
    sq, gap = CW - 2, 2
    ph = CH / 2
    cream = mode == 'two'
    bubbles_at = set()
    for k2 in range(4):
        tt = (t + k2 / 4) % 1.0
        bx, by = int(blow[0] * GW + 0.6 * math.sin(6 * tt + k2)), int(blow[1] * GH - tt * 12)
        if by >= 0: bubbles_at.add((bx, by))
    for gy in range(GH):
        for gx in range(GW):
            reg, cov = grid[gy][gx]
            lv = level(reg, cov, gy)
            ramp = RAMP_ORANGE if mode == 'orange' else RAMP_TEAL
            if cream and reg in (BELLY, FIN) and lv:
                ramp, lv = RAMP_CREAM, 3 if cov > 0.65 else 2
            if lv == 0:
                # quiet "commit" noise in the water, drifting left
                for nx, ny, z in NOISE_CELLS:
                    if (int(nx - t * GW * 0.5) % GW, ny) == (gx, gy):
                        lv = 1 if z < 0.75 else 2
                        break
            col = ramp[lv]
            if (gx, gy) in bubbles_at and reg == BG:
                col = C['orange'] if mode != 'orange' else C['bright']
            x, y = ox + gx * CW + 1, oy + gy * ph + 1
            d.rounded_rectangle((x, y, x + sq, y + ph - gap), 2, fill=col)


def r_pix_outline(img, ox, oy, t):
    """pixel art with a dark outline, 3-band shading, eye highlight"""
    d = ImageDraw.Draw(img)
    grid, blow = sample(t)
    ph = CH / 2
    OUTL = (5, 15, 18)
    occ = [[grid[y][x][0] != BG and grid[y][x][1] >= 0.35 for x in range(GW)] for y in range(GH)]
    for i, (px, py, z) in enumerate(DUST[:30]):
        x, y = int(((px - t * (0.2 + 0.5 * z)) % 1.0) * GW), int(py * GH)
        if not occ[y][x] and i % 2:
            d.rectangle((ox + x * CW + 4, oy + y * ph + 3, ox + x * CW + 6, oy + y * ph + 5), fill=lerp(C['base'], C['teal'], 0.3 + 0.5 * z))
    for gy in range(GH):
        for gx in range(GW):
            reg, cov = grid[gy][gx]
            if not occ[gy][gx]:
                # outline ring around the body
                if any(0 <= gx + dx < GW and 0 <= gy + dy < GH and occ[gy + dy][gx + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    d.rectangle((ox + gx * CW, oy + gy * ph, ox + gx * CW + CW - 1, oy + gy * ph + ph - 1), fill=OUTL)
                continue
            yf = gy / GH
            if reg in (BELLY, FIN):
                c = C['text'] if reg == FIN or (gy + 1 < GH and occ[gy + 1][gx]) else hexc('#b9b29a')
            elif reg == GROOVE:
                c = hexc('#b9b29a')
            elif reg == EYE:
                c = OUTL
            elif reg == EDGE:
                c = hexc('#9fd0d6') if yf < 0.45 else hexc('#2a6f79')
            else:
                c = hexc('#6fb3bd') if yf < 0.36 else (C['teal'] if yf < 0.47 else hexc('#2a6f79'))
            d.rectangle((ox + gx * CW, oy + gy * ph, ox + gx * CW + CW - 1, oy + gy * ph + ph - 1), fill=c)
            if reg == EYE:
                d.rectangle((ox + gx * CW + CW - 4, oy + gy * ph + 1, ox + gx * CW + CW - 2, oy + gy * ph + 3), fill=C['bright'])
    for k2 in range(4):
        tt = (t + k2 / 4) % 1.0
        bx, by = int(blow[0] * GW), int(blow[1] * GH - tt * 12)
        if by >= 0:
            d.rectangle((ox + bx * CW + 2, oy + by * ph + 1, ox + bx * CW + CW - 3, oy + by * ph + ph - 2), outline=C['bright'])


def r_pix_chunky(img, ox, oy, t):
    """big 2x2 retro pixels (19 x 14), sunset water band behind"""
    d = ImageDraw.Draw(img)
    W2, H2 = GW // 2, GH // 2
    grid, blow = sample(t, W2, H2, 12)
    bw, bh = CW * 2, CH
    for gy in range(H2):
        for gx in range(W2):
            reg, cov = grid[gy][gx]
            x, y = ox + gx * bw, oy + gy * bh
            if reg == BG or cov < 0.4:
                # dithered dusk water: teal top -> mauve bottom, sparse
                if (gx + gy * 3 + int(t * 8)) % 7 == 0:
                    d.rectangle((x + 8, y + 9, x + 12, y + 13), fill=lerp(C['deep'], C['mauve'], gy / H2))
                continue
            if reg in (BELLY, FIN, GROOVE): c = C['text']
            elif reg == EYE: c = C['base']
            elif reg == EDGE: c = C['bright'] if gy < H2 * 0.45 else C['deep']
            else: c = C['teal'] if gy < H2 * 0.47 else C['deep']
            d.rectangle((x, y, x + bw - 2, y + bh - 2), fill=c)
    tt = t % 1.0
    bx, by = int(blow[0] * W2), int(blow[1] * H2 - tt * 6)
    if by >= 0:
        d.rectangle((ox + bx * bw + 6, oy + by * bh + 6, ox + bx * bw + bw - 8, oy + by * bh + bh - 8), outline=C['orange'], width=2)


STYLES = [('G1', 'GitHub graph · teal levels — whale "committed" into the grid', lambda i, x, y, t: r_github(i, x, y, t, 'teal')),
          ('G2', 'GitHub graph · orange levels — the flower colour', lambda i, x, y, t: r_github(i, x, y, t, 'orange')),
          ('G3', 'GitHub graph · teal body + cream belly, orange bubbles', lambda i, x, y, t: r_github(i, x, y, t, 'two')),
          ('C1', 'Pixel art (your C) — flat colours, square bubbles', r_pixels),
          ('C2', 'Pixel art · outlined sprite, 3-tone shading, eye shine', r_pix_outline),
          ('C3', 'Pixel art · chunky retro 2×2, dusk dither water', r_pix_chunky)]


def sheet2(t):
    tiles = [kitty(fn, t, name) for key, name, fn in STYLES]
    tw, th = tiles[0].size
    pad, head = 24, 54
    out = Image.new('RGB', (pad + 2 * (tw + pad), head + 3 * (th + 44 + pad)), C['base'])
    d = ImageDraw.Draw(out)
    fg = ImageFont.truetype(MONO + 'Bold.otf', 22)
    fs = ImageFont.truetype(MONO + 'Regular.otf', 15)
    d.text((pad, 16), 'kitty greeting — whale round 2 (70×20). Pick one', fill=C['bright'], font=fg)
    for i, ((key, name, fn), tile) in enumerate(zip(STYLES, tiles)):
        x, y = pad + (i % 2) * (tw + pad), head + (i // 2) * (th + 44 + pad)
        d.text((x, y + 10), key, fill=C['orange'], font=fg)
        d.text((x + 44, y + 13), name, fill=C['text'], font=fs)
        out.paste(tile, (x, y + 44))
    return out


sheet2(0.15).save(OUT + 'whale-styles2.png')
frames = [sheet2(i / 16) for i in range(16)]
small = [f.resize((f.width * 3 // 5, f.height * 3 // 5), Image.LANCZOS).convert('P', palette=Image.ADAPTIVE, colors=128) for f in frames]
small[0].save(OUT + 'whale-styles2.gif', save_all=True, append_images=small[1:], duration=110, loop=0, optimize=True)
print('ok')
