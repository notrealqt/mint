#!/usr/bin/env python3
# Mockups: top panel + a maximised Firefox on the laptop screen.
# Source: preview/full.png (flameshot full). Output: preview/panel-max-*.png
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, PH = 3072, 1728, 80                       # laptop px, panel height px
full = Image.open('preview/full.png').convert('RGB')
desk = full.crop((0, 0, W, H))
ff_src = full.crop((5000, 0, 6932, 2160))        # Firefox window on the ViewSonic
ff = ff_src.resize((W, int(ff_src.height * W / ff_src.width)), Image.LANCZOS)
TITLE = int(64 * W / ff_src.width)               # Firefox's title-bar height after scaling
ISLANDS = [(12, 775), (1380, 1692), (2338, 3058)]
IY0, IY1, R = 8, 72, 28
BASE, ISLE, LINE, ORANGE = (11, 29, 34), (11, 37, 44), (44, 74, 80), (227, 146, 54)
font = ImageFont.truetype('/home/notrealqt/.local/share/fonts/Geist/Geist-SemiBold.ttf', 40)
small = ImageFont.truetype('/usr/local/share/fonts/Geist/Geist-Regular.ttf', 30)


def rmask(size, box, r):
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, r, fill=255)
    return m


def islands(img, bg, border, flat=False):
    """Paste the real island contents onto a new strip background."""
    d = ImageDraw.Draw(img)
    for x0, x1 in ISLANDS:
        box = (x0, IY0, x1, IY1)
        if flat:
            d.rectangle((x0, 0, x1, PH), fill=bg)
        else:
            d.rounded_rectangle(box, R, fill=ISLE, outline=border, width=2)
        inner = (x0 + 3, IY0 + 3, x1 - 3, IY1 - 3)
        img.paste(desk.crop(inner), inner[:2], rmask((inner[2] - inner[0], inner[3] - inner[1]),
                                                     (0, 0, inner[2] - inner[0] - 1, inner[3] - inner[1] - 1), R - 3))


def caption(img, title, sub):
    d = ImageDraw.Draw(img, 'RGBA')
    d.rounded_rectangle((W - 1460, H - 190, W - 40, H - 40), 24, fill=(11, 29, 34, 235), outline=LINE, width=2)
    d.text((W - 1420, H - 172), title, font=font, fill=ORANGE)
    d.text((W - 1420, H - 112), sub, font=small, fill=(232, 223, 198))


def save(img, name):
    img.resize((W // 2, H // 2), Image.LANCZOS).save(f'preview/{name}.png')
    return img


shots = []

# A · now: clear strip (wallpaper peeks between the islands) + Firefox title bar + tabs + nav
a = desk.copy()
a.paste(ff.crop((0, 0, W, H - PH)), (0, PH))
caption(a, 'A · now', 'wallpaper slivers, then 4 stacked dark bands')
shots.append(save(a, 'panel-max-a-now'))

# B · merge: strip goes solid when a window is maximised, islands melt into one flat bar
#     the same colour as Firefox's tab strip; maximised windows lose their title bar
b = Image.new('RGB', (W, H), (9, 22, 25))
b.paste(ff.crop((0, TITLE, W, TITLE + H - PH)), (0, PH))
islands(b, (9, 22, 25), None, flat=True)
caption(b, 'B · merge when maximised', 'panel + tabs read as one header; islands come back on the desktop')
shots.append(save(b, 'panel-max-b-merge'))

# C · docked islands: strip solid base, islands keep their pill shape, no title bar
c = Image.new('RGB', (W, H), BASE)
c.paste(ff.crop((0, TITLE, W, TITLE + H - PH)), (0, PH))
ImageDraw.Draw(c).line((0, PH - 1, W, PH - 1), fill=LINE, width=2)
islands(c, BASE, LINE)
caption(c, 'C · solid strip, islands kept', 'same look everywhere; hairline under the panel')
shots.append(save(c, 'panel-max-c-docked'))

# D · floating window: wallpaper strip stays, a maximised window gets a 16px gap,
#     rounded corners and a shadow, like the islands; no title bar
d = desk.copy()
G = 16
box = (G, PH + 4, W - G, H - G)
sh = Image.new('L', (W, H), 0)
ImageDraw.Draw(sh).rounded_rectangle((box[0], box[1] + 10, box[2], box[3] + 10), 28, fill=170)
d.paste((0, 0, 0), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))
win = ff.crop((0, TITLE, box[2] - box[0], TITLE + box[3] - box[1]))
d.paste(win, box[:2], rmask(win.size, (0, 0, win.width - 1, win.height - 1), 28))
ImageDraw.Draw(d).rounded_rectangle(box, 28, outline=LINE, width=2)
caption(d, 'D · floating window', 'gap all round, rounded like the islands')
shots.append(save(d, 'panel-max-d-float'))

# 2x2 sheet
sheet = Image.new('RGB', (W + 24, H + 24), BASE)
for i, s in enumerate(shots):
    sheet.paste(s.resize((W // 2, H // 2), Image.LANCZOS), ((i % 2) * (W // 2 + 24), (i // 2) * (H // 2 + 24)))
sheet.save('preview/panel-max-sheet.png')
