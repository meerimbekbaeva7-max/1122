"""Instagram reel: talking head (enhanced) + muted work B-roll as a voice-over slot + end card.
Frames are composed in Python (zoom punches, captions, labels) and piped to ffmpeg."""
import subprocess, json, numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.signal import butter, sosfilt, resample_poly
W, H, FPS = 1080, 1920, 30
D = '/home/user/1122/reel_pol/'
FB = '/usr/share/fonts/opentype/inter/'
font = lambda name, s: ImageFont.truetype(FB + name, s)
F_CAP, F_TITLE, F_LBL, F_SMALL, F_BTN = font('InterDisplay-Black.otf', 76), font('InterDisplay-Black.otf', 118), font('InterDisplay-ExtraBold.otf', 58), font('Inter-SemiBold.otf', 38), font('InterDisplay-ExtraBold.otf', 50)
GOLD, YEL, WA = (241, 196, 92), (255, 214, 64), (37, 211, 102)
T0 = 0.45                                   # trim dead air before the first word (speech starts at 0.68)
TALK = 13.866 - T0
# phrases with times in the source (from word timings)
PH = [(0.68, 1.55, 'Ээ, туугандар!'), (1.55, 2.16, 'Ассалому алейкум,'), (2.16, 3.55, 'урматтуу Бишкек шаарынын тургундары!'),
      (3.55, 4.95, 'Бүгүн биз ангардабыз,'), (4.95, 6.62, 'куйма таш кызматын кылып жатабыз.'),
      (6.62, 9.0, 'Эгерде биздин кызмат сиздерге кызык боло турган болсо,'), (9.0, 11.4, 'төмөндөгү WhatsApp номерине кайрыла бериңиздер.'),
      (11.4, 13.5, 'Жана ошондой эле биздин ишти көрө кетиңиздер.')]
ZOOM = [1.0, 1.08, 1.0, 1.12, 1.03, 1.08, 1.18, 1.05]
KEY = {'Бишкек', 'куйма', 'таш', 'WhatsApp', 'ишти'}
# B-roll: (file, start, dur, label)
BR = [('work1.mp4', 7.0, 2.0, 'Куябыз'), ('work1.mp4', 9.3, 1.8, 'Тегиздейбиз'), ('work2.mp4', 4.6, 1.8, 'Бурчтарга чейин так'),
      ('work1.mp4', 19.2, 2.0, 'Жылмакай, тигишсиз бет'), ('work2.mp4', 12.0, 1.8, 'Ийне ролик — көбүкчөлөр чыгат'),
      ('work1.mp4', 24.4, 1.6, 'Коргоочу катмар'), ('work1.mp4', 28.3, 2.0, 'Соккуга чыдамдуу'),
      ('work1.mp4', 31.0, 2.4, 'Маркер калбайт — оңой тазаланат'), ('work2.mp4', 15.0, 2.2, 'Суу өткөрбөйт'),
      ('work2.mp4', 24.0, 2.0, 'Түсүн өзүңүз тандайсыз')]
BRD = sum(b[2] for b in BR)
END = 3.6
TOTAL = TALK + BRD + END
logo = Image.open(D + 'logo.png').convert('RGBA')

def reader(args):
    p = subprocess.Popen(['ffmpeg', '-v', 'error'] + args + ['-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield Image.frombuffer('RGB', (W, H), b)

GRADE = 'eq=contrast=1.08:saturation=1.15:gamma=0.98,colorbalance=rs=.02:bs=-.02,unsharp=5:5:0.7'
def clip(f, s, d):
    return reader(['-ss', str(s), '-t', str(d), '-i', D + f, '-vf', f'scale={W}:{H}:flags=lanczos,fps={FPS},{GRADE}', '-an'])

def text_box(draw, xy, txt, fnt, fill, stroke=8, sfill=(0, 0, 0), anchor='mm'):
    draw.text(xy, txt, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=sfill, anchor=anchor)

def wrap(words, fnt, maxw, draw):
    lines, cur = [], []
    for w in words:
        t = ' '.join(cur + [w])
        if draw.textlength(t, font=fnt) > maxw and cur: lines.append(cur); cur = [w]
        else: cur.append(w)
    if cur: lines.append(cur)
    return lines

def caption(img, t_src):
    d = ImageDraw.Draw(img)
    for i, (a, b, txt) in enumerate(PH):
        if a <= t_src < b + .12:
            words = txt.split(); n = len(words)
            k = min(n - 1, int((t_src - a) / max(.01, b - a) * n))          # current word (proportional)
            lines = wrap(words, F_CAP, W - 140, d)
            y0 = int(H * .7) - (len(lines) - 1) * 46
            pop = min(1, (t_src - a) / .12)
            idx = 0
            for li, ln in enumerate(lines):
                full = ' '.join(ln); x = (W - d.textlength(full, font=F_CAP)) / 2
                for w in ln:
                    on = idx == k; key = w.strip(',.!').replace('ң', 'ң') in KEY
                    col = YEL if on or key else (255, 255, 255)
                    d.text((x, y0 + li * 92 + (0 if pop >= 1 else (1 - pop) * 20)), w, font=F_CAP, fill=col, stroke_width=9, stroke_fill=(0, 0, 0), anchor='lm')
                    x += d.textlength(w + ' ', font=F_CAP); idx += 1
            return i
    return -1

def badge(img, x, y, txt, fnt, bg, fg=(255, 255, 255), pad=(34, 18), r=40, alpha=235):
    lay = Image.new('RGBA', img.size); d = ImageDraw.Draw(lay)
    tw = d.textlength(txt, font=fnt); bb = fnt.getbbox(txt); th = bb[3] - bb[1]
    box = [x - tw / 2 - pad[0], y - th / 2 - pad[1], x + tw / 2 + pad[0], y + th / 2 + pad[1] + 6]
    d.rounded_rectangle(box, r, fill=bg + (alpha,)); d.text((x, y + 3), txt, font=fnt, fill=fg, anchor='mm')
    img.alpha_composite(lay)

def wa_icon(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255)); d.polygon([(cx - r * .75, cy + r * .55), (cx - r * 1.05, cy + r * 1.05), (cx - r * .25, cy + r * .9)], fill=(255, 255, 255))
    d.ellipse([cx - r * .72, cy - r * .72, cx + r * .72, cy + r * .72], fill=WA)
    d.rounded_rectangle([cx - r * .38, cy - r * .42, cx - r * .1, cy + r * .05], r * .1, fill=(255, 255, 255)); d.rounded_rectangle([cx - r * .1, cy + r * .12, cx + r * .4, cy + r * .4], r * .1, fill=(255, 255, 255))

def logo_at(img, cx, cy, s, a=1.0):
    lg = logo.resize((s, s), Image.LANCZOS)
    if a < 1: lg.putalpha(lg.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lg, (int(cx - s / 2), int(cy - s / 2)))

def progress(img, t):
    d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 10], fill=(0, 0, 0, 90)); d.rectangle([0, 0, int(W * t / TOTAL), 10], fill=GOLD + (255,))

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', D + 'video_silent.mp4'], stdin=subprocess.PIPE)
fi = 0; cuts = []
def emit(img):
    global fi
    enc.stdin.write(img.convert('RGB').tobytes()); fi += 1

# ---- part 1: talking head with zoom punches and captions ----
talk = reader(['-ss', str(T0), '-i', D + 'a_video.mp4'])
for n, fr in enumerate(talk):
    t = n / FPS; ts = t + T0
    if t >= TALK: break
    seg = max([i for i, p in enumerate(PH) if ts >= p[0]] or [0])
    z = ZOOM[seg] + (.02 * (ts - PH[seg][0]) if seg in (2, 7) else 0)        # slow push on long phrases
    if z > 1.001:
        cw, ch = W / z, H / z; cx, cy = W / 2, H * .36
        x0 = min(max(0, cx - cw / 2), W - cw); y0 = min(max(0, cy - ch * .36), H - ch)
        fr = fr.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)
    img = fr.convert('RGBA')
    # top gradient for legibility
    g = Image.linear_gradient('L').resize((W, 420)).transpose(Image.FLIP_TOP_BOTTOM).point(lambda v: int(v * .55))
    img.paste((0, 0, 0), (0, 0, W, 420), g)
    if t < 3.2:
        a = min(1, t / .25) * (1 if t < 2.8 else (3.2 - t) / .4)
        lay = Image.new('RGBA', img.size); d = ImageDraw.Draw(lay)
        text_box(d, (W / 2, 230), 'КУЙМА ПОЛ', F_TITLE, GOLD + (int(255 * a),), stroke=10, sfill=(0, 0, 0, int(255 * a)))
        text_box(d, (W / 2, 340), 'Бишкек • сапаттуу кызмат', F_SMALL, (255, 255, 255, int(255 * a)), stroke=5, sfill=(0, 0, 0, int(255 * a)))
        img.alpha_composite(lay)
    else:
        logo_at(img, 110, 120, 150, .95)
    caption(img, ts)
    if 9.4 <= ts < 13.9:                                                       # WhatsApp call-out
        k = min(1, (ts - 9.4) / .25); y = int(H * .86) + int((1 - k) * 60)
        lay = Image.new('RGBA', img.size); d = ImageDraw.Draw(lay)
        d.rounded_rectangle([170, y - 62, W - 170, y + 62], 62, fill=WA + (int(240 * k),)); wa_icon(d, 250, y, 34)
        d.text((W / 2 + 40, y + 2), 'WhatsApp — жазыңыз', font=F_BTN, fill=(255, 255, 255, int(255 * k)), anchor='mm')
        img.alpha_composite(lay)
    progress(img, t); emit(img)
cuts.append(fi / FPS)

# ---- part 2: muted work B-roll (voice-over slot) ----
for bi, (f, s, dur, lbl) in enumerate(BR):
    for n, fr in enumerate(clip(f, s, dur)):
        t = n / FPS
        if t >= dur: break
        z = 1.06 - .05 * (t / dur) if bi % 2 else 1.0 + .05 * (t / dur)           # gentle push/pull per shot
        cw, ch = W / z, H / z; fr = fr.crop((int((W - cw) / 2), int((H - ch) / 2), int((W + cw) / 2), int((H + ch) / 2))).resize((W, H), Image.LANCZOS)
        img = fr.convert('RGBA')
        if t < .1:                                                               # white flash on the cut
            img.alpha_composite(Image.new('RGBA', img.size, (255, 255, 255, int(150 * (1 - t / .1)))))
        k = min(1, t / .18)
        lay = Image.new('RGBA', img.size); d = ImageDraw.Draw(lay)
        tw = d.textlength(lbl, font=F_LBL); y = int(H * .78)
        d.rounded_rectangle([W / 2 - tw / 2 - 40, y - 56, W / 2 + tw / 2 + 40, y + 56], 28, fill=(16, 14, 12, int(200 * k)))
        d.rectangle([W / 2 - tw / 2 - 40, y - 56, W / 2 - tw / 2 - 28, y + 56], fill=GOLD + (int(255 * k),))
        d.text((W / 2 + 6, y + 2), lbl, font=F_LBL, fill=(255, 255, 255, int(255 * k)), anchor='mm')
        img.alpha_composite(lay)
        if bi == 0 and t < 1.6:
            badge(img, W / 2, 210, 'БИЗДИН ИШТЕР', F_LBL, (16, 14, 12), GOLD)
        logo_at(img, W - 110, 120, 150, .95); progress(img, fi / FPS); emit(img)
    cuts.append(fi / FPS)

# ---- part 3: end card ----
last = list(clip('work2.mp4', 20.0, .1))[0].filter(ImageFilter.GaussianBlur(18)).convert('RGBA')
last.alpha_composite(Image.new('RGBA', last.size, (8, 7, 6, 165)))
for n in range(int(END * FPS)):
    t = n / FPS; img = last.copy(); k = min(1, t / .35)
    logo_at(img, W / 2, 560, int(330 + 30 * k), k)
    lay = Image.new('RGBA', img.size); d = ImageDraw.Draw(lay)
    d.text((W / 2, 850), 'КУЙМА ПОЛ', font=F_TITLE, fill=GOLD + (int(255 * k),), anchor='mm', stroke_width=6, stroke_fill=(0, 0, 0, int(200 * k)))
    d.text((W / 2, 955), 'көп жыл кызмат кылат — пол көйгөйлөрүн унутасыз', font=F_SMALL, fill=(255, 255, 255, int(240 * k)), anchor='mm')
    k2 = min(1, max(0, (t - .3) / .3)); y = 1180
    d.rounded_rectangle([150, y - 70, W - 150, y + 70], 70, fill=WA + (int(250 * k2),)); wa_icon(d, 240, y, 38)
    d.text((W / 2 + 55, y + 2), 'WhatsApp аркылуу жазыңыз', font=font('InterDisplay-ExtraBold.otf', 43), fill=(255, 255, 255, int(255 * k2)), anchor='mm')
    k3 = min(1, max(0, (t - .6) / .3)); y = 1360
    for x0, x1, txt, col, fg in [(150, 525, 'Жазылыңыз', (225, 48, 108), (255, 255, 255)), (555, W - 150, 'Кененирээк', (245, 242, 236), (20, 18, 16))]:
        d.rounded_rectangle([x0, y - 58, x1, y + 58], 58, fill=col + (int(245 * k3),))
        d.text(((x0 + x1) / 2, y + 2), txt, font=F_BTN, fill=fg + (int(255 * k3),), anchor='mm')
    s = 1 + .06 * np.sin(t * 6) if t > 1 else 1
    d.text((W / 2, 1520), 'Лайк басыңыз', font=font('InterDisplay-ExtraBold.otf', int(48 * s)), fill=(255, 255, 255, int(230 * k3)), anchor='mm')
    img.alpha_composite(lay); progress(img, fi / FPS); emit(img)
enc.stdin.close(); enc.wait()
json.dump({'talk': TALK, 'cuts': cuts, 'total': fi / FPS}, open(D + 'timeline.json', 'w'))
print('frames', fi, 'dur', fi / FPS, 'cuts', [round(c, 2) for c in cuts])
