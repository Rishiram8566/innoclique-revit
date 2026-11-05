#!/usr/bin/env python3
"""
train_wall_model.py - trains the small neural network used by innoclique_site.py.

WHAT IT LEARNS
  For every dark pixel on a drawing, decide: is this pixel a WALL, or is it
  something else (text, dimension lines, grid lines, furniture, door swings,
  window lines, hatching, title block, scan noise)?
  The page then removes the non-wall pixels before it builds walls, rooms and
  the 3D model, and before it compares a Revit PDF/image against CAD.

DATA
  No labelled floor-plan dataset is bundled, so this script GENERATES one:
  random room layouts (solid, double-line, hatched and thin walls, with doors
  and windows) plus the clutter listed above, at random sizes, blur and noise.
  The wall label comes from the generator, so it is exact.

MODEL
  Input : 13x13 pixel patch around the pixel + a 9x9 wider patch (3x zoomed out)
          = 250 numbers.
  Net   : 250 -> 32 -> 16 -> 1 (ReLU, sigmoid). About 8.5k weights. Pure numpy.
  Output: wall_model.json (the page reads it; innoclique_site.py also embeds it).

RUN     python train_wall_model.py            (about 3-6 minutes, numpy+scipy+Pillow)
        python train_wall_model.py --quick    (1 minute smoke test)
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi

FINE, COARSE, CS = 13, 9, 3
NF = FINE * FINE + COARSE * COARSE  # 250
LAYERS = [NF, 32, 16, 1]
CAND = 0.25  # a pixel with ink above this is a candidate wall pixel


# --------------------------------------------------------------------------
# 1. synthetic floor-plan generator
# --------------------------------------------------------------------------
_fonts = {}


def font(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.load_default(size=size)
    return _fonts[size]


WORDS = ["BED", "BED 1", "BED 2", "LIVING", "KITCHEN", "BATH", "WC", "HALL", "STORE",
         "OFFICE", "LOBBY", "UTILITY", "DINING", "GARAGE", "STUDY", "W.I.C", "ENTRY"]


def rand_label(rng):
    k = rng.integers(0, 4)
    if k == 0:
        return str(rng.choice(WORDS))
    if k == 1:
        return f"{rng.uniform(2, 9):.1f} x {rng.uniform(2, 9):.1f}"
    if k == 2:
        return f"{rng.integers(8, 60)} m2"
    return f"{rng.integers(100, 9999)}"


def make_plan(seed):
    """Return (ink float32 HxW in 0..1, wall bool HxW)."""
    rng = np.random.default_rng(seed)
    S = int(rng.integers(384, 769))
    if rng.random() < .5:
        W, H = S, int(S * rng.uniform(.6, 1.0))
    else:
        W, H = int(S * rng.uniform(.6, 1.0)), S
    mn, mx = min(W, H), max(W, H)
    mgn = int(rng.uniform(.10, .18) * mn)
    x0, y0, x1, y1 = mgn, mgn, W - mgn, H - mgn
    style = str(rng.choice(["solid", "double", "hatch", "thin"], p=[.3, .3, .2, .2]))
    t = int(rng.integers(2, 4)) if style == "thin" else max(4, int(rng.uniform(.008, .022) * mx))
    h2 = t // 2

    band = Image.new("L", (W, H), 0)
    bd = ImageDraw.Draw(band)
    other = Image.new("L", (W, H), 0)
    di = ImageDraw.Draw(other)

    def hwall(xa, xb, y):
        bd.rectangle([xa - h2, y - h2, xb + h2, y - h2 + t - 1], fill=255)

    def vwall(x, ya, yb):
        bd.rectangle([x - h2, ya - h2, x - h2 + t - 1, yb + h2], fill=255)

    hwall(x0, x1, y0); hwall(x0, x1, y1); vwall(x0, y0, y1); vwall(x1, y0, y1)
    rooms, parts = [], []

    def split(rx0, ry0, rx1, ry1, depth):
        w, h = rx1 - rx0, ry1 - ry0
        minr = int(.16 * mx)
        cv, ch = w > 2 * minr, h > 2 * minr
        if depth >= 4 or (not cv and not ch) or (depth >= 2 and rng.random() < .25):
            rooms.append((rx0, ry0, rx1, ry1)); return
        vertical = ((w > h) if rng.random() < .7 else rng.random() < .5) if (cv and ch) else cv
        p = rng.uniform(.38, .62)
        if vertical:
            x = int(rx0 + p * w); vwall(x, ry0, ry1); parts.append(("v", x, ry0, ry1))
            split(rx0, ry0, x, ry1, depth + 1); split(x, ry0, rx1, ry1, depth + 1)
        else:
            y = int(ry0 + p * h); hwall(rx0, rx1, y); parts.append(("h", y, rx0, rx1))
            split(rx0, ry0, rx1, y, depth + 1); split(rx0, y, rx1, ry1, depth + 1)

    split(x0, y0, x1, y1, 0)

    # doors in partitions: cut the wall band and draw the swing (not wall)
    for kind, pos, a, b in parts:
        g = max(int(rng.uniform(.035, .06) * mx), 2 * t)
        if b - a < 3.4 * g:
            continue
        for _ in range(1 + int((b - a) > 7 * g and rng.random() < .5)):
            c = int(rng.uniform(a + .8 * g, b - 1.8 * g))
            if kind == "v":
                bd.rectangle([pos - h2 - 1, c, pos - h2 + t, c + g], fill=0)
                if rng.random() < .85:
                    hy_top = rng.random() < .5
                    hx, hy = pos, (c if hy_top else c + g)
                    ac = 90 if hy_top else 270
                    al = int(rng.choice([0, 180]))
                    draw_swing(di, rng, hx, hy, g, ac, al)
            else:
                bd.rectangle([c, pos - h2 - 1, c + g, pos - h2 + t], fill=0)
                if rng.random() < .85:
                    hx_left = rng.random() < .5
                    hx, hy = (c if hx_left else c + g), pos
                    ac = 0 if hx_left else 180
                    al = int(rng.choice([90, 270]))
                    draw_swing(di, rng, hx, hy, g, ac, al)
    # front door and windows on the outer wall
    g = max(int(.05 * mx), 2 * t)
    c = int(rng.uniform(x0 + g, x1 - 2 * g))
    bd.rectangle([c, y1 - h2 - 1, c + g, y1 - h2 + t], fill=0)
    for _ in range(int(rng.integers(0, 4))):
        wl = int(.08 * mx)
        side = int(rng.integers(0, 3))
        if side == 0:
            c = int(rng.uniform(x0 + wl, x1 - 2 * wl))
            bd.rectangle([c, y0 - h2 - 1, c + wl, y0 - h2 + t], fill=0)
            for yy in (y0 - h2, y0, y0 - h2 + t - 1):
                di.line([c, yy, c + wl, yy], fill=255, width=1)
        elif side == 1:
            c = int(rng.uniform(y0 + wl, y1 - 2 * wl))
            bd.rectangle([x0 - h2 - 1, c, x0 - h2 + t, c + wl], fill=0)
            for xx in (x0 - h2, x0, x0 - h2 + t - 1):
                di.line([xx, c, xx, c + wl], fill=255, width=1)
        else:
            c = int(rng.uniform(y0 + wl, y1 - 2 * wl))
            bd.rectangle([x1 - h2 - 1, c, x1 - h2 + t, c + wl], fill=0)
            for xx in (x1 - h2, x1, x1 - h2 + t - 1):
                di.line([xx, c, xx, c + wl], fill=255, width=1)

    wall = np.array(band) > 0

    # how the walls are drawn
    if style in ("solid", "thin"):
        wink = wall.astype(np.float32)
    else:
        we = int(rng.integers(1, 3))
        er = ndi.binary_erosion(wall, iterations=we)
        wink = (wall & ~er).astype(np.float32)
        if style == "hatch":
            sp = int(rng.integers(4, 9))
            yy, xx = np.mgrid[:H, :W]
            wink = np.maximum(wink, (((xx + yy) % sp == 0) & er).astype(np.float32))

    # clutter: furniture, stairs, text, dims, grid, frame
    for rx0, ry0, rx1, ry1 in rooms:
        rw, rh = rx1 - rx0, ry1 - ry0
        if rng.random() < .65:
            for _ in range(int(rng.integers(1, 4))):
                fw = int(rng.uniform(.15, .4) * rw); fh = int(rng.uniform(.15, .4) * rh)
                if fw < 8 or fh < 8:
                    continue
                fx = int(rng.uniform(rx0 + 2 * t, max(rx0 + 2 * t + 1, rx1 - fw - 2 * t)))
                fy = int(rng.uniform(ry0 + 2 * t, max(ry0 + 2 * t + 1, ry1 - fh - 2 * t)))
                lw = int(rng.integers(1, 3))
                if rng.random() < .3:
                    di.ellipse([fx, fy, fx + fw, fy + fh], outline=255, width=lw)
                else:
                    di.rectangle([fx, fy, fx + fw, fy + fh], outline=255, width=lw)
                    if rng.random() < .3:
                        di.line([fx, fy, fx + fw, fy + fh], fill=255, width=1)
        if rng.random() < .15 and rw > 60 and rh > 60:  # stairs: parallel thin lines
            sx, sy = int(rx0 + .2 * rw), int(ry0 + .2 * rh)
            sw, sh = int(.3 * rw), int(.35 * rh)
            step = int(rng.integers(5, 9))
            for yy in range(sy, sy + sh, step):
                di.line([sx, yy, sx + sw, yy], fill=255, width=1)
            di.rectangle([sx, sy, sx + sw, sy + sh], outline=255, width=1)
        if rng.random() < .75:
            fs = int(rng.integers(9, 21))
            di.text(((rx0 + rx1) // 2, (ry0 + ry1) // 2), rand_label(rng), fill=255,
                    font=font(fs), anchor="mm")

    # dimension chains above and left of the plan
    if rng.random() < .75:
        yd = y0 - int(rng.uniform(.45, .8) * mgn)
        xs = sorted([x0, x1] + [p[1] for p in parts if p[0] == "v"])
        di.line([x0, yd, x1, yd], fill=255, width=1)
        for xa, xb in zip(xs[:-1], xs[1:]):
            di.line([xb, yd - 7, xb, yd + 7], fill=255, width=1)
            di.line([xb, y0 - 3, xb, yd - 7], fill=255, width=1)
            di.text(((xa + xb) // 2, yd - 8), f"{(xb - xa) * rng.uniform(8, 14):.0f}", fill=255,
                    font=font(int(rng.integers(8, 13))), anchor="mb")
        di.line([xs[0], yd - 7, xs[0], yd + 7], fill=255, width=1)
        xd = x0 - int(rng.uniform(.45, .8) * mgn)
        di.line([xd, y0, xd, y1], fill=255, width=1)
        for yy in (y0, y1):
            di.line([xd - 7, yy, xd + 7, yy], fill=255, width=1)
    if rng.random() < .4:  # dashed grid lines + bubbles
        for kind, pos, a, b in parts:
            if kind != "v":
                continue
            ya, yb = y0 - int(.6 * mgn), y1 + int(.6 * mgn)
            for yy in range(ya, yb, 15):
                di.line([pos, yy, pos, min(yy + 10, yb)], fill=255, width=1)
            di.ellipse([pos - 9, ya - 18, pos + 9, ya], outline=255, width=1)
    if rng.random() < .5:  # frame + title block
        ins = int(rng.integers(3, 9))
        di.rectangle([ins, ins, W - ins, H - ins], outline=255, width=int(rng.integers(1, 4)))
        if rng.random() < .6:
            bw, bh = int(.28 * W), int(.08 * H)
            di.rectangle([W - ins - bw, H - ins - bh, W - ins, H - ins], outline=255, width=int(rng.integers(1, 3)))
            di.line([W - ins - bw, H - ins - bh // 2, W - ins, H - ins - bh // 2], fill=255, width=1)
            di.text((W - ins - bw // 2, H - ins - bh // 4), "SHEET A-101", fill=255, font=font(10), anchor="mm")

    ink = np.maximum(wink, np.array(other, dtype=np.float32) / 255.0)
    ink *= rng.uniform(.6, 1.0)
    if rng.random() < .6:
        ink = ndi.gaussian_filter(ink, rng.uniform(.3, .9))
    ink += rng.normal(0, rng.uniform(0, .03), ink.shape)
    for _ in range(int(rng.integers(0, 60))):  # scan speckles
        sx, sy, sr = rng.integers(0, W), rng.integers(0, H), int(rng.integers(0, 2))
        ink[max(0, sy - sr):sy + sr + 1, max(0, sx - sr):sx + sr + 1] = rng.uniform(.4, 1.0)
    ink = np.clip(ink, 0, 1).astype(np.float32)
    label = ndi.binary_dilation(wall, iterations=1)
    return ink, label


def draw_swing(di, rng, hx, hy, g, ac, al):
    d = (ac - al) % 360
    start, end = (al, ac) if d == 90 else (ac, al)
    di.arc([hx - g, hy - g, hx + g, hy + g], start % 360, end % 360, fill=255, width=1)
    ex, ey = hx + g * np.cos(np.radians(al)), hy + g * np.sin(np.radians(al))
    di.line([hx, hy, ex, ey], fill=255, width=int(rng.integers(1, 3)))


# --------------------------------------------------------------------------
# 2. features (must match innoclique_site.py exactly)
# --------------------------------------------------------------------------
def feats(ink, ys, xs):
    n = len(ys)
    pf, pc = FINE // 2, (COARSE // 2) * CS
    padf = np.pad(ink, pf)
    d1 = np.arange(-pf, pf + 1)
    f1 = padf[ys[:, None, None] + pf + d1[None, :, None],
              xs[:, None, None] + pf + d1[None, None, :]].reshape(n, -1)
    b3 = ndi.uniform_filter(ink, size=3, mode="constant", cval=0.0)
    padc = np.pad(b3, pc)
    d2 = np.arange(-(COARSE // 2), COARSE // 2 + 1) * CS
    f2 = padc[ys[:, None, None] + pc + d2[None, :, None],
              xs[:, None, None] + pc + d2[None, None, :]].reshape(n, -1)
    return np.concatenate([f1, f2], 1).astype(np.float32)


# --------------------------------------------------------------------------
# 3. tiny MLP in numpy (Adam)
# --------------------------------------------------------------------------
class MLP:
    def __init__(self, rng):
        self.P = []
        for a, b in zip(LAYERS[:-1], LAYERS[1:]):
            self.P += [(rng.normal(0, np.sqrt(2 / a), (a, b))).astype(np.float32), np.zeros(b, np.float32)]
        self.m = [np.zeros_like(p) for p in self.P]
        self.v = [np.zeros_like(p) for p in self.P]
        self.t = 0

    def forward(self, X, keep=False):
        W1, b1, W2, b2, W3, b3 = self.P
        z1 = X @ W1 + b1; a1 = np.maximum(z1, 0)
        z2 = a1 @ W2 + b2; a2 = np.maximum(z2, 0)
        z3 = (a2 @ W3 + b3)[:, 0]
        p = 1 / (1 + np.exp(-np.clip(z3, -30, 30)))
        return (p, (X, z1, a1, z2, a2)) if keep else p

    def step(self, X, y, lr, wd=1e-5):
        p, (X, z1, a1, z2, a2) = self.forward(X, True)
        W1, b1, W2, b2, W3, b3 = self.P
        n = len(y)
        d3 = ((p - y) / n)[:, None]
        g = [None] * 6
        g[4] = a2.T @ d3; g[5] = d3.sum(0)
        d2 = (d3 @ W3.T) * (z2 > 0)
        g[2] = a1.T @ d2; g[3] = d2.sum(0)
        d1 = (d2 @ W2.T) * (z1 > 0)
        g[0] = X.T @ d1; g[1] = d1.sum(0)
        self.t += 1
        for i, (prm, gr) in enumerate(zip(self.P, g)):
            if i % 2 == 0:
                gr = gr + wd * prm
            self.m[i] = .9 * self.m[i] + .1 * gr
            self.v[i] = .999 * self.v[i] + .001 * gr * gr
            mh = self.m[i] / (1 - .9 ** self.t); vh = self.v[i] / (1 - .999 ** self.t)
            prm -= (lr * mh / (np.sqrt(vh) + 1e-8)).astype(np.float32)


def bce(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean())


# --------------------------------------------------------------------------
# 4. data + evaluation helpers
# --------------------------------------------------------------------------
def sample_set(seeds, per_class, rng):
    X, Y = [], []
    for s in seeds:
        ink, lab = make_plan(s)
        ys, xs = np.nonzero(ink > CAND)
        l = lab[ys, xs]
        pos, neg = np.nonzero(l)[0], np.nonzero(~l)[0]
        take = []
        for idx in (pos, neg):
            if len(idx):
                take.append(rng.choice(idx, min(per_class, len(idx)), replace=False))
        if not take:
            continue
        take = np.concatenate(take)
        X.append(feats(ink, ys[take], xs[take])); Y.append(l[take].astype(np.float32))
    return np.concatenate(X), np.concatenate(Y)


def dense_eval(model, seeds):
    """natural-distribution predictions on every candidate pixel of each image"""
    out = []
    for s in seeds:
        ink, lab = make_plan(s)
        cand = ink > CAND
        ys, xs = np.nonzero(cand)
        p = model.forward(feats(ink, ys, xs))
        l = lab[ys, xs]
        comp, _ = ndi.label(cand)
        sizes = np.bincount(comp.ravel())
        base = sizes[comp[ys, xs]] >= 6  # the page's old rule: drop specks under 6 px
        out.append((p, l, base))
    return out


def prf(pred, lab):
    tp = int((pred & lab).sum()); fp = int((pred & ~lab).sum()); fn = int((~pred & lab).sum())
    pr = tp / max(tp + fp, 1); rc = tp / max(tp + fn, 1)
    return dict(precision=pr, recall=rc, f1=2 * pr * rc / max(pr + rc, 1e-9), iou=tp / max(tp + fp + fn, 1))


def metrics(ev, cut):
    P = np.concatenate([e[0] for e in ev]); L = np.concatenate([e[1] for e in ev]); B = np.concatenate([e[2] for e in ev])
    return dict(model=prf(P >= cut, L), keep_everything=prf(np.ones_like(L), L), speck_filter=prf(B, L), wall_share=float(L.mean()))


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default=str(Path(__file__).with_name("wall_model.json")))
    a = ap.parse_args()
    n_tr, n_va, n_te, per, epochs = (60, 12, 20, 500, 8) if a.quick else (380, 50, 100, 700, 30)
    rng = np.random.default_rng(7)
    t0 = time.time()
    print(f"generating {n_tr} training plans ...")
    Xtr, Ytr = sample_set(range(1000, 1000 + n_tr), per, rng)
    Xva, Yva = sample_set(range(50000, 50000 + n_va), per, rng)
    print(f"  {len(Ytr):,} training pixels, {len(Yva):,} validation pixels ({time.time() - t0:.0f}s)")

    net = MLP(rng)
    best, best_P = 9, None
    for ep in range(epochs):
        lr = 2e-3 * (0.5 * (1 + np.cos(np.pi * ep / epochs)) * .95 + .05)
        order = rng.permutation(len(Ytr))
        for i in range(0, len(order), 1024):
            b = order[i:i + 1024]
            net.step(Xtr[b], Ytr[b], lr)
        vl = bce(net.forward(Xva), Yva)
        if vl < best:
            best, best_P = vl, [p.copy() for p in net.P]
        print(f"  epoch {ep + 1:2d}/{epochs}  val loss {vl:.4f}")
    net.P = best_P

    # round weights exactly as stored, and evaluate THAT model
    R = 4
    net.P = [np.round(p, R).astype(np.float32) for p in net.P]
    print("choosing the confidence cut on held-out validation plans ...")
    ev_va = dense_eval(net, range(50000, 50000 + n_va))
    cuts = np.arange(.2, .81, .05)
    f1s = [metrics(ev_va, c)["model"]["f1"] for c in cuts]
    cut = float(round(cuts[int(np.argmax(f1s))], 2))
    print(f"  best cut {cut}")

    print(f"testing on {n_te} unseen plans ...")
    m = metrics(dense_eval(net, range(90000, 90000 + n_te)), cut)
    for k in ("model", "speck_filter", "keep_everything"):
        v = m[k]
        print(f"  {k:16s} precision {v['precision']:.3f}  recall {v['recall']:.3f}  F1 {v['f1']:.3f}  IoU {v['iou']:.3f}")

    W1, b1, W2, b2, W3, b3 = [np.round(p.astype(np.float64), R) for p in net.P]  # clean 4-decimal numbers
    model = dict(
        fine=FINE, coarse=COARSE, cs=CS, layers=LAYERS, cut=cut, cand=CAND,
        W1=W1.ravel().tolist(), b1=b1.tolist(), W2=W2.ravel().tolist(), b2=b2.tolist(),
        W3=W3.ravel().tolist(), b3=b3.tolist(),
        meta=dict(train_plans=n_tr, train_pixels=int(len(Ytr)), test_plans=n_te, data="synthetic",
                  test=m, params=int(sum(p.size for p in net.P))))
    Path(a.out).write_text(json.dumps(model, separators=(",", ":")))
    print(f"wrote {a.out}  ({Path(a.out).stat().st_size / 1024:.0f} KB, {model['meta']['params']:,} weights)  total {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()