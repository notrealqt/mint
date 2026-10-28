#!/usr/bin/env python3
# Mockups for panel B ("merge when a window touches the panel") in the cases that
# aren't a maximised Firefox. Uses make_panel_mocks.py's sources. Output: preview/panel-case-*.png
from PIL import Image, ImageDraw, ImageFilter
import importlib.util, sys
spec = importlib.util.spec_from_file_location('m', 'preview/make_panel_mocks.py')
sys.argv = ['x']
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
W, H, PH, ff, desk, TITLE = m.W, m.H, m.PH, m.ff, m.desk, m.TITLE
HEAD = (16, 37, 43)                      # window title-bar colour = merged panel colour
kitty = m.full.crop((36, 280, 1536, 1324))   # this kitty window on the laptop


def recolor_tabs(img):
    """Firefox tab strip (#091619) → title-bar colour, so it matches the merged panel."""
    px = img.load()
    for y in range(0, int(150 * W / 1932)):
        for x in range(img.width):
            r, g, b = px[x, y]
            if abs(r - 9) < 4 and abs(g - 22) < 4 and abs(b - 25) < 4:
                px[x, y] = HEAD
    return img


ffm = recolor_tabs(ff.crop((0, TITLE, W, TITLE + H)).copy())


def strip_merged(img):
    ImageDraw.Draw(img).rectangle((0, 0, W, PH - 1), fill=HEAD)
    m.islands(img, HEAD, None, flat=True)


def shadowed(img, box, win, r=24, top_round=True):
    sh = Image.new('L', (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle((box[0], box[1] + 12, box[2], box[3] + 12), r, fill=160)
    img.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(24)))
    img.paste(win, box[:2], m.rmask(win.size, (0, 0, win.width - 1, win.height - 1), r))


shots = []

# 1 · tiled left (Super+←): window touches the panel → whole strip merges
a = desk.copy()
strip_merged(a)
a.paste(ffm.crop((0, 0, W // 2, H - PH)), (0, PH))
ImageDraw.Draw(a).line((W // 2, PH, W // 2, H), fill=m.LINE, width=2)
m.caption(a, '1 · tiled half (Super+←)', 'touches the panel → whole strip merges')
shots.append(m.save(a, 'panel-case-1-tiled'))

# 2 · floating window, not touching → islands as usual
b = desk.copy()
box = (520, 300, 2420, 1500)
shadowed(b, box, ffm.crop((0, 0, box[2] - box[0], box[3] - box[1])))
m.caption(b, '2 · normal window, gap above', 'nothing touches → floating islands stay')
shots.append(m.save(b, 'panel-case-2-float'))

# 3 · floating window dragged up against the panel → counts as touching
c = desk.copy()
strip_merged(c)
box = (520, PH, 2420, 1300)
shadowed(c, box, ffm.crop((0, 0, box[2] - box[0], box[3] - box[1])), r=1)
m.caption(c, '3 · window pushed up to the top', 'top edge within 8px of the panel → merges')
shots.append(m.save(c, 'panel-case-3-touch'))

# 4 · maximised kitty (normal title bar): title bar is the same colour as the merged strip
d = Image.new('RGB', (W, H), HEAD)
strip_merged(d)
kb = kitty.getpixel((400, 400))
ImageDraw.Draw(d).rectangle((0, PH + 60, W, H), fill=kb)
title = kitty.crop((300, 0, 1200, 60))
d.paste(title, ((W - title.width) // 2, PH))
d.paste(kitty.crop((0, 60, kitty.width, kitty.height)), (0, PH + 60))
m.caption(d, '4 · maximised terminal / files', 'panel + title bar = one header')
shots.append(m.save(d, 'panel-case-4-kitty'))

sheet = Image.new('RGB', (W + 24, H + 24), m.BASE)
for i, s in enumerate(shots):
    sheet.paste(s.resize((W // 2, H // 2), Image.LANCZOS), ((i % 2) * (W // 2 + 24), (i // 2) * (H // 2 + 24)))
sheet.save('preview/panel-case-sheet.png')
