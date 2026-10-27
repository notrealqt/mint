# Doorway rice — mockup of the redesigned conky card (Wi-Fi and wired states).
# python3 -I ~/rice/preview/make_card_mock.py  ->  ~/rice/preview/card-v3.png
from PIL import Image, ImageDraw, ImageFont, ImageFilter

K = 2  # draw at 2x so it's easy to read
F = '/home/notrealqt/.local/share/fonts/GeistMonoNF/GeistMonoNerdFont-'
def G(w, s): return ImageFont.truetype(F + w + '.otf', s * K)
C = dict(base=(11, 29, 34), line=(44, 74, 80), overlay=(29, 59, 66), muted=(124, 145, 150), text=(232, 223, 198),
         bright=(242, 229, 184), teal=(79, 154, 166), orange=(227, 146, 54), amber=(215, 134, 21),
         mauve=(179, 154, 171), olive=(154, 165, 86), red=(205, 92, 69))

W, PAD, COL2, LBL = 380, 20, 196, 64
bg = Image.open('/home/notrealqt/Pictures/wallhaven-vp2l1m_1920x1080.png').convert('RGBA')
bg = bg.crop((1050, 0, 1920, 760)).resize((870 * K, 760 * K))
ov = Image.new('RGBA', bg.size, (0, 0, 0, 0))
d = ImageDraw.Draw(ov)


def t(x, y, s, c='text', f=None):
    d.text((x * K, y * K), s, fill=C[c] + (255,), font=f or G('Regular', 13))


def tr(x, y, s, c='text', f=None):
    f = f or G('Regular', 13)
    d.text((x * K - d.textlength(s, font=f), y * K), s, fill=C[c] + (255,), font=f)


def card(x0, y0, rows_fn):
    # measure by drawing into a throwaway, then draw for real
    h = rows_fn(x0, y0, dry=True) - y0 + PAD
    box = (x0 * K, y0 * K, (x0 + W) * K, (y0 + h) * K)
    bg.paste(bg.crop(box).filter(ImageFilter.GaussianBlur(16 * K)), box[:2])
    d.rounded_rectangle(box, 12 * K, fill=C['base'] + (222,), outline=C['line'] + (255,), width=K)
    rows_fn(x0, y0, dry=False)


def build(state):
    def rows(x0, y0, dry):
        global t, tr
        real_t, real_tr = t, tr
        if dry:
            t = tr = lambda *a, **k: None
        x, y, R = x0 + PAD, y0 + PAD, x0 + W - PAD

        def section(title, meta=''):
            nonlocal y
            y += 10
            f = G('SemiBold', 11)
            t(x, y, title, 'orange', f)
            tw = d.textlength(title, font=f) / K
            mw = d.textlength(meta, font=G('Regular', 11)) / K if meta else 0
            if not dry:
                d.line([((x + tw + 8) * K, (y + 8) * K), ((R - mw - (8 if meta else 0)) * K, (y + 8) * K)], fill=C['line'] + (255,), width=K)
            if meta: tr(R, y, meta, 'muted', G('Regular', 11))
            y += 22

        def kv(l1, v1, c1='text', l2=None, v2=None, c2='text'):
            nonlocal y
            t(x, y, l1, 'muted'); t(x + LBL, y, v1, c1)
            if l2: t(x + COL2, y, l2, 'muted'); t(x + COL2 + LBL, y, v2, c2)
            y += 20

        # header
        t(x, y, 'notrealqt', 'bright', G('SemiBold', 17))
        pill = '● online'
        f = G('Medium', 11); pw = d.textlength(pill, font=f) / K
        if not dry:
            d.rounded_rectangle([(R - pw - 16) * K, (y + 1) * K, R * K, (y + 21) * K], 10 * K, fill=C['overlay'] + (255,))
        t(R - pw - 8, y + 4, pill, 'olive', f)
        y += 26
        t(x, y, 'up 3h 12m  ·  mint 22.2  ·  cinnamon', 'muted', G('Regular', 11)); y += 16

        section('SYSTEM')
        kv('cpu', '5%  51°', 'text', 'ram', '6.1 / 15 G')
        kv('ssd', '15%  37°', 'text', 'bat', '100%')
        kv('amd', '13%  47°', 'text', 'nvi', 'zz', 'muted')
        kv('fan', '2200 · 3200', 'text', 'mode', 'performance', 'mauve')

        if state == 'wifi':
            section('LINK', 'wifi  wlp3s0')
            kv('ssid', 'TQT 5G', 'text', 'sig', '50%', 'amber')
            kv('band', '5 GHz · ch 44', 'text', 'rate', '866 Mb/s')
            kv('ap', 'a4:2b:b0:1c:7e:9e', 'muted')
        else:
            section('LINK', 'wired  enp2s0')
            kv('speed', '1 Gb/s full', 'olive', 'vlan', '20')
            kv('switch', 'core-sw1 (Cisco 9300)')
            kv('port', 'Gi1/0/14 · "desk-3F-12"', 'mauve')

        section('NETWORK')
        kv('lan', '192.168.1.24/24' if state == 'wifi' else '10.20.0.57/24')
        kv('gw', '192.168.1.1' if state == 'wifi' else '10.20.0.1')
        kv('dns', '192.168.1.1  · 12 ms' if state == 'wifi' else '10.0.0.53  · 3 ms')
        kv('wan', '1.53.27.230  VN · Viettel')
        kv('vpn', '○ off' if state == 'wifi' else '● wg0 10.8.0.3', 'muted' if state == 'wifi' else 'olive',
           'fw', '● ufw on', 'olive')
        y += 2
        t(x, y, '↓ 1.2 MB/s', 'teal', G('Medium', 13)); t(x + COL2, y, '↑ 40 KB/s', 'orange', G('Medium', 13)); y += 20

        section('HEALTH')
        t(x, y - 4, '', 'muted'); tr(R - 112, y, 'ms', 'muted', G('Regular', 11)); tr(R - 52, y, 'loss', 'muted', G('Regular', 11)); tr(R, y, 'jitter', 'muted', G('Regular', 11)); y += 18
        rows_ = [('gw', '1', '0%', '0.3', 'olive'), ('1.1.1.1', '34', '0%', '2.1', 'olive'), ('google', '60', '0%', '4.8', 'olive')]
        if state == 'wired':
            rows_ = [('gw', '1', '0%', '0.1', 'olive'), ('1.1.1.1', '9', '0%', '0.6', 'olive'), ('google', '96', '3%', '18', 'amber')]
        for name, ms, loss, jit, c in rows_:
            t(x, y, '●', c); t(x + 18, y, name)
            tr(R - 112, y, ms, c); tr(R - 52, y, loss, 'text' if loss == '0%' else 'amber'); tr(R, y, jit, 'text' if c == 'olive' else 'amber')
            y += 20

        section('CONNECTIONS')
        kv('est', '25', 'text', 'listen', '13')
        kv('ssh-in', '0' if state == 'wifi' else '1  from 10.20.0.9', 'text' if state == 'wifi' else 'red')
        kv('top', 'chrome 13', 'mauve', ' ', 'code 6', 'mauve')
        kv('exposed', '—' if state == 'wifi' else ':22 ssh (open to network)', 'muted' if state == 'wifi' else 'amber')

        if dry:
            t, tr = real_t, real_tr
        return y
    return rows


card(40, 30, build('wifi'))
card(450, 30, build('wired'))
t(40, 8, 'on wifi', 'bright', G('Medium', 12))
t(450, 8, 'plugged into a switch (example)', 'bright', G('Medium', 12))
Image.alpha_composite(bg, ov).convert('RGB').save('/home/notrealqt/rice/preview/card-v3.png')
print('ok')
