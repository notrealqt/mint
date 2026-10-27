# Doorway rice — whale "G1+" : GitHub-contribution-graph whale with more movement.
# Seamless loop (every effect is periodic in t). python3 -I make_whale_g1.py -> whale-g1.gif / whale-g1.png
import random
src = open('/home/notrealqt/rice/preview/make_whale_mock2.py').read().split('STYLES = [')[0]
exec(src)
# smaller whale so the wake behind the tail stays on screen (redefines whale_mask with L = 0.66 W)
_m1 = open('/home/notrealqt/rice/preview/make_whale_mock.py').read()
_wm = _m1[_m1.index('def whale_mask'):_m1.index('def particles')]
exec(_wm.replace('L = 0.80 * W', 'L = 0.66 * W'))

TEAL = RAMP_TEAL                         # 0 empty .. 4 brightest


def level(reg, cov, gy):
    # whale always brighter than the water (water/rays use 1, wake 1-2)
    if reg in (BG, EYE) or cov < 0.3:
        return 0
    if reg == EDGE:
        return 4
    if reg in (BELLY, FIN):
        return 3 if cov > 0.6 else 2
    if reg == GROOVE:
        return 2
    return 3 if cov > 0.6 else 2
SPARK = [C['orange'], hexc('#f5bd66'), C['bright']]
FR = 40                                  # frames per loop
rnd = random.Random(21)
WATER = [(rnd.randrange(GW), rnd.randrange(GH), rnd.random()) for _ in range(34)]
BUB = [(rnd.random(), rnd.random()) for _ in range(5)]


def whale_at(t):
    # two tail strokes per loop; small forward/back surge
    return sample((2 * t) % 1.0)


def tail_cell(t):
    """approx. tail-joint cell at phase t (for the wake)"""
    ph = 2 * math.pi * ((2 * t) % 1.0)
    L = 0.66 * GW
    x = GW * 0.90 - L * 1.0
    y = GH * 0.47 + 0.02 * L * math.sin(ph) + L * (0.05 * math.sin(ph - 3.0))
    return x, y


def frame(t):
    grid, blow = whale_at(t)
    lv = [[0] * GW for _ in range(GH)]
    col = [[None] * GW for _ in range(GH)]
    # 1. water: drifting quiet commits (scroll one full width per loop → seamless)
    for x, y, z in WATER:
        gx = int(x - t * GW) % GW
        lv[y][gx] = max(lv[y][gx], 1)
    # 2. light rays: diagonal band sweeping left→right
    band = (t * (GW + GH) * 1.0) % (GW + GH) - GH
    for gy in range(GH):
        for gx in range(GW):
            dd = (gx + gy * 0.6) - band - GH * 0.3
            if -1.0 < dd < 1.0:
                lv[gy][gx] = max(lv[gy][gx], 1)
    # 3. wake behind the tail: past tail positions drifting left, fading
    for j in range(1, 16):
        tp = (t - j / FR) % 1.0
        tx, ty = tail_cell(tp)
        tx -= j * 0.75 + 4.5                  # starts behind the flukes, drifts away with the water
        for off in (-1, 0, 1):
            gx, gy = int(round(tx)), int(round(ty + off * (1 + j * 0.12) + math.sin(j * 1.3)))
            if 0 <= gx < GW and 0 <= gy < GH and (off == 0 or j > 3):
                lv[gy][gx] = max(lv[gy][gx], 2 if j < 9 else 1)
    # 4. the whale
    for gy in range(GH):
        for gx in range(GW):
            reg, cov = grid[gy][gx]
            l = level(reg, cov, gy)
            if l:
                lv[gy][gx] = l
                col[gy][gx] = 'whale'
            if reg == EYE and cov > 0.1:
                lv[gy][gx] = 0
                col[gy][gx] = 'eye'
    bx, by = blow[0] * GW, blow[1] * GH
    # 5. bubbles from the mouth side, brightening before they pop
    for k, (o, w) in enumerate(BUB):
        tt = (t * 2 + o) % 1.0
        gx = int(bx + 3 + w * 3 + math.sin(tt * 9 + k)) % GW
        gy = int(by + 4 - tt * 16)
        if 0 <= gy < GH and col[gy][gx] is None:
            lv[gy][gx] = 2 if tt < 0.7 else 4
    # 6. spout once per loop (t 0.55..0.9): fountain up then falling spray
    if 0.55 <= t < 0.9:
        u = (t - 0.55) / 0.35
        h = 9 * math.sin(math.pi * min(1, u * 1.4))
        for i in range(int(h)):
            gy = int(by) - 1 - i
            if gy >= 0:
                lv[gy][int(bx)] = 5 + (i > h - 3)
                col[gy][int(bx)] = 'spark'
        if u > 0.35:
            spread = (u - 0.35) / 0.65
            for side in (-1, 1):
                for k in range(4):
                    gx = int(bx + side * (1 + k * 0.8 + spread * 4))
                    gy = int(by - 9 + 1 + spread * spread * 9 + k * 0.7)
                    if 0 <= gx < GW and 0 <= gy < GH and col[gy][gx] is None:
                        lv[gy][gx] = 5
                        col[gy][gx] = 'spark'
    return lv, col


def draw_grid(img, ox, oy, t):
    d = ImageDraw.Draw(img)
    lv, col = frame(t)
    ph = CH / 2
    for gy in range(GH):
        for gx in range(GW):
            l = lv[gy][gx]
            if col[gy][gx] == 'spark':
                c = SPARK[min(2, l - 5)] if l >= 5 else SPARK[0]
            elif col[gy][gx] == 'eye':
                c = C['base']
            else:
                c = TEAL[min(4, l)]
            x, y = ox + gx * CW + 1, oy + gy * ph + 1
            d.rounded_rectangle((x, y, x + CW - 3, y + ph - 3), 2, fill=c)


def kitty_g1(t):
    W, H = COLS * CW + 40, ROWS * CH + 40
    img = Image.new('RGB', (W, H), C['base'])
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(MONO + 'Regular.otf', 17)
    fb = ImageFont.truetype(MONO + 'Bold.otf', 17)
    fsm = ImageFont.truetype(MONO + 'Regular.otf', 14)
    ox, oy = 20, 20
    d.text((ox, oy + 2), 'whale contributions', fill=C['text'], font=fsm)
    d.text((ox + 17 * CW, oy + 2), '· last 38 weeks', fill=C['muted'], font=fsm)
    draw_grid(img, ox, oy + CH, t)
    ly = oy + CH + GH * CH / 2 + 6
    d.text((ox + 22 * CW, ly), 'Less', fill=C['muted'], font=fsm)
    for i in range(5):
        x = ox + 26.5 * CW + i * CW
        d.rounded_rectangle((x, ly + 4, x + CW - 3, ly + 4 + CH / 2 - 3), 2, fill=TEAL[i])
    d.text((ox + 32 * CW, ly), 'More', fill=C['muted'], font=fsm)
    ix = ox + (WC + 3) * CW
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


frames = [kitty_g1(i / FR) for i in range(FR)]
big = [f.resize((f.width * 3 // 2, f.height * 3 // 2), Image.NEAREST) for f in frames]
big[0].save(OUT + 'whale-g1.gif', save_all=True, append_images=big[1:], duration=90, loop=0, optimize=True)
# contact strip of 4 moments for a quick look
strip = Image.new('RGB', (frames[0].width * 2 + 30, frames[0].height * 2 + 30), C['base'])
for k, i in enumerate((2, 14, 26, 32)):
    strip.paste(frames[i], (10 + (k % 2) * (frames[0].width + 10), 10 + (k // 2) * (frames[0].height + 10)))
strip.save(OUT + 'whale-g1.png')
print('ok')
