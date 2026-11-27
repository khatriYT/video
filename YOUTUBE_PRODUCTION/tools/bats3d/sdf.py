#!/usr/bin/env python3
"""Signed-distance-field modeller (numpy, runs in system Python, outside Blender).

Characters are sculpted as exact SDFs (smooth unions/subtractions of ellipsoids, round cones,
tori, rounded boxes, shells), meshed with vectorised Surface Nets, relaxed with Taubin smoothing
(no shrinkage), and written as small binary files that Blender loads (tools/bats3d/meshio.py).

python3 tools/bats3d/sdf.py <out_dir> pip|farmer|researcher|bats
"""
import math
import os
import struct
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skeleton as SK  # noqa: E402


# ------------------------------------------------------------------ primitives (P: (n,3) array)
def _v(a):
    return np.asarray(a, dtype=np.float64)


def sphere(P, c, r):
    return np.linalg.norm(P - _v(c), axis=1) - r


def ellipsoid(P, c, r, R=None):
    """Approximate SDF (Quilez). R: 3x3 rotation whose COLUMNS are the local axes in world space."""
    q = P - _v(c)
    if R is not None:
        q = q @ _v(R)
    r = _v(r)
    k0 = np.linalg.norm(q / r, axis=1)
    k1 = np.linalg.norm(q / (r * r), axis=1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


def rcone(P, a, b, ra, rb):
    """Round cone / capsule between a (radius ra) and b (radius rb)."""
    a, b = _v(a), _v(b)
    ba = b - a
    L2 = ba @ ba
    pa = P - a
    t = np.clip((pa @ ba) / max(L2, 1e-12), 0.0, 1.0)
    d = np.linalg.norm(pa - t[:, None] * ba, axis=1)
    return d - (ra + (rb - ra) * t)


def capsule(P, a, b, r):
    return rcone(P, a, b, r, r)


def polyline(P, pts, radii):
    d = None
    for i in range(len(pts) - 1):
        x = rcone(P, pts[i], pts[i + 1], radii[i], radii[i + 1])
        d = x if d is None else np.minimum(d, x)
    return d


def torus(P, c, axis, R, r):
    q = P - _v(c)
    ax = _v(axis) / np.linalg.norm(axis)
    h = q @ ax
    rad = np.linalg.norm(q - h[:, None] * ax, axis=1)
    return np.sqrt((rad - R) ** 2 + h ** 2) - r


def rbox(P, c, half, R=None, rr=0.0):
    q = P - _v(c)
    if R is not None:
        q = q @ _v(R)
    d = np.abs(q) - (_v(half) - rr)
    return np.linalg.norm(np.maximum(d, 0.0), axis=1) + np.minimum(d.max(axis=1), 0.0) - rr


def plane(P, n, d0):
    n = _v(n) / np.linalg.norm(n)
    return P @ n - d0


# ------------------------------------------------------------------ operators
def smin(a, b, k):
    if k <= 0:
        return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b + (a - b) * h - k * h * (1.0 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def sub(a, b, k=0.0):
    """a minus b."""
    return smax(a, -b, k)


def shell(d, t):
    return np.abs(d) - t


def wrinkles(P, amp, freq, seed=0, n=6):
    rng = np.random.default_rng(seed)
    w = np.zeros(len(P))
    for i in range(n):
        k = rng.normal(size=3)
        k = k / np.linalg.norm(k) * freq * rng.uniform(0.6, 1.4)
        w += np.sin(P @ k + rng.uniform(0, 6.283)) / n
    return w * amp


def rot_cols(x, y, z):
    """3x3 with columns = local x, y, z axes (orthonormalised)."""
    x = _v(x) / np.linalg.norm(x)
    z = np.cross(x, _v(y))
    z = z / np.linalg.norm(z)
    y = np.cross(z, x)
    return np.stack([x, y, z], axis=1)


def rotz(deg):
    a = math.radians(deg)
    return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])


def rotx(deg):
    a = math.radians(deg)
    return np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])


def roty(deg):
    a = math.radians(deg)
    return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])


# ------------------------------------------------------------------ meshing
def surface_nets(fn, lo, hi, h, chunk=400000):
    lo, hi = _v(lo), _v(hi)
    n = np.ceil((hi - lo) / h).astype(int) + 1
    gx, gy, gz = [lo[i] + np.arange(n[i]) * h for i in range(3)]
    G = np.stack(np.meshgrid(gx, gy, gz, indexing="ij"), axis=-1).reshape(-1, 3)
    f = np.concatenate([fn(G[i:i + chunk]) for i in range(0, len(G), chunk)]).reshape(n)
    s = f < 0
    nx, ny, nz = n
    corners = [(i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    cv = [f[i:nx - 1 + i, j:ny - 1 + j, k:nz - 1 + k] for i, j, k in corners]
    cs = [c < 0 for c in cv]
    anyin = np.zeros_like(cs[0])
    allin = np.ones_like(cs[0])
    for c in cs:
        anyin |= c
        allin &= c
    mixed = anyin & ~allin
    idx = np.argwhere(mixed)
    acc = np.zeros((len(idx), 3))
    cnt = np.zeros(len(idx))
    sel = tuple(idx.T)
    edges = [(a, b) for a in range(8) for b in range(a + 1, 8)
             if sum(abs(corners[a][t] - corners[b][t]) for t in range(3)) == 1]
    for a, b in edges:
        fa, fb = cv[a][sel], cv[b][sel]
        m = (fa < 0) != (fb < 0)
        t = fa[m] / (fa[m] - fb[m])
        pa, pb = _v(corners[a]), _v(corners[b])
        acc[m] += pa + t[:, None] * (pb - pa)
        cnt[m] += 1
    vpos = lo + (idx + acc / np.maximum(cnt, 1)[:, None]) * h
    vid = -np.ones(mixed.shape, dtype=np.int64)
    vid[sel] = np.arange(len(idx))
    faces = []
    for ax in range(3):
        o1, o2 = [(1, 2), (2, 0), (0, 1)][ax]
        sl0 = [slice(None)] * 3
        sl1 = [slice(None)] * 3
        sl0[ax] = slice(0, n[ax] - 1)
        sl1[ax] = slice(1, n[ax])
        for d in (o1, o2):
            sl0[d] = slice(1, n[d] - 1)
            sl1[d] = slice(1, n[d] - 1)
        a = s[tuple(sl0)]
        b = s[tuple(sl1)]
        m = a != b
        e = np.argwhere(m)
        e[:, o1] += 1
        e[:, o2] += 1
        flip = ~a[m]

        def cell(d1, d2):
            c = e.copy()
            c[:, o1] -= d1
            c[:, o2] -= d2
            return vid[tuple(c.T)]
        q = np.stack([cell(1, 1), cell(0, 1), cell(0, 0), cell(1, 0)], axis=1)
        q[flip] = q[flip][:, ::-1]
        faces.append(q)
    F = np.concatenate(faces)
    F = F[(F >= 0).all(axis=1)]
    return vpos, F


def taubin(V, F, iters=6, lam=0.5, mu=-0.53, mask=None):
    n = len(V)
    E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 3]], F[:, [3, 0]]])
    E = np.unique(np.sort(E, axis=1), axis=0)
    deg = np.bincount(E.ravel(), minlength=n).astype(float)
    for _ in range(iters):
        for f in (lam, mu):
            acc = np.zeros_like(V)
            np.add.at(acc, E[:, 0], V[E[:, 1]])
            np.add.at(acc, E[:, 1], V[E[:, 0]])
            avg = acc / np.maximum(deg, 1)[:, None]
            w = f if mask is None else f * mask[:, None]
            V = V + (avg - V) * w
    return V


def write(path, V, F, attrs=None):
    attrs = np.zeros((len(V), 0)) if attrs is None else np.asarray(attrs, dtype=np.float32).reshape(len(V), -1)
    with open(path, "wb") as fh:
        fh.write(struct.pack("<iii", len(V), len(F), attrs.shape[1]))
        fh.write(np.asarray(V, dtype=np.float32).tobytes())
        fh.write(np.asarray(F, dtype=np.int32).tobytes())
        fh.write(attrs.astype(np.float32).tobytes())
    print(f"  {os.path.basename(path)}: {len(V)} verts, {len(F)} quads", flush=True)


BONES = None


def skin_weights(V, allowed, power=4.0, eps=0.01, topk=3):
    """Inverse-distance weights to bone segments -> (n, 2*topk) array [ids..., weights...]."""
    global BONES
    if BONES is None:
        BONES = {b[0]: (i, _v(b[1]), _v(b[2])) for i, b in enumerate(SK.bones())}
    ids = [BONES[n][0] for n in allowed]
    D = []
    for n in allowed:
        _, a, b = BONES[n]
        ba = b - a
        t = np.clip(((V - a) @ ba) / (ba @ ba), 0, 1)
        D.append(np.linalg.norm(V - (a + t[:, None] * ba), axis=1))
    D = np.stack(D, axis=1)
    W = 1.0 / (D + eps) ** power
    k = min(topk, W.shape[1])
    order = np.argsort(-W, axis=1)[:, :k]
    Wk = np.take_along_axis(W, order, axis=1)
    Wk /= Wk.sum(axis=1, keepdims=True)
    I = np.array(ids)[order]
    if k < topk:
        I = np.concatenate([I, np.full((len(V), topk - k), I[:, :1])], axis=1)
        Wk = np.concatenate([Wk, np.zeros((len(V), topk - k))], axis=1)
    return np.concatenate([I.astype(np.float32), Wk.astype(np.float32)], axis=1)


def dense_weights(V, allowed, power=4.0, eps=0.01):
    global BONES
    if BONES is None:
        BONES = {b[0]: (i, _v(b[1]), _v(b[2])) for i, b in enumerate(SK.bones())}
    D = []
    for n in allowed:
        _, a, b = BONES[n]
        ba = b - a
        t = np.clip(((V - a) @ ba) / (ba @ ba), 0, 1)
        D.append(np.linalg.norm(V - (a + t[:, None] * ba), axis=1))
    W = 1.0 / (np.stack(D, 1) + eps) ** power
    return W / W.sum(1, keepdims=True)


def encode_weights(names, W, topk=3):
    ids = np.array([BONES[n][0] for n in names])
    k = min(topk, W.shape[1])
    order = np.argsort(-W, axis=1)[:, :k]
    Wk = np.take_along_axis(W, order, axis=1)
    Wk /= np.maximum(Wk.sum(axis=1, keepdims=True), 1e-9)
    return np.concatenate([ids[order].astype(np.float32), Wk.astype(np.float32)], axis=1)


def shirt_weights(V):
    """Sleeve surfaces follow the arm, torso surfaces the spine; blended where they meet (armpit/shoulder)."""
    torso = ["pelvis", "spine", "chest", "neck"]
    names = torso + ["shoulder.L", "upperarm.L", "shoulder.R", "upperarm.R"]
    Wt = np.concatenate([dense_weights(V, torso, 4.0, 0.03), np.zeros((len(V), 4))], 1)
    dt = torso_body(V, 0.006)
    out = Wt.copy()
    for sx, s, col in ((1, "L", 4), (-1, "R", 6)):
        sh, el = _v(SK.mirror(SK.SH, sx)), _v(SK.mirror(SK.EL, sx))
        ds = rcone(V, sh, sh + (el - sh) * 0.86, 0.056, 0.05)
        a = np.clip((dt - ds) / 0.025 + 0.5, 0, 1)
        # along the arm: shoulder near the joint, upper arm further down
        u = np.clip(((V - sh) @ (el - sh)) / ((el - sh) @ (el - sh)), 0, 1)
        wa = np.zeros((len(V), 8))
        wa[:, col] = np.clip(1 - u * 4, 0, 1) * 0.6
        wa[:, col + 1] = 1 - wa[:, col]
        out = out * (1 - a[:, None]) + wa * a[:, None]
        # shoulder blend: torso vertices near the shoulder take a little of the clavicle
        near = np.exp(-np.sum((V - sh) ** 2, 1) / (2 * 0.05 ** 2)) * (1 - a)
        out[:, col] += near * 0.5
    out /= out.sum(1, keepdims=True)
    return encode_weights(names, out)


MANIFEST = []


def mesh(path, fn, lo, hi, h, smooth=6, attr_fn=None, mask_fn=None, bones=("head",), power=4.0, eps=0.01,
         mat=None, local=None):
    """Mesh an SDF part and record it in the manifest. bones: allowed bones for skinning.
    local: an offset (head-local parts) applied before weighting."""
    V, F = surface_nets(fn, lo, hi, h)
    V = taubin(V, F, smooth, mask=None if mask_fn is None else mask_fn(V))
    A = None if attr_fn is None else np.asarray(attr_fn(V), dtype=np.float32).reshape(len(V), -1)
    Vw = V + (_v(local) if local is not None else 0.0)
    Wt = skin_weights(Vw, list(bones), power, eps) if bones != "shirt" else shirt_weights(Vw)
    natt = 0 if A is None else A.shape[1]
    write(path, V, F, Wt if A is None else np.concatenate([A, Wt], axis=1))
    MANIFEST.append(dict(file=os.path.basename(path), mat=mat or os.path.basename(path)[:-4], tint=natt,
                         local=list(local) if local is not None else None,
                         bones=list(bones) if bones != "shirt" else "shirt"))
    return V, F


# ------------------------------------------------------------------ v3 human models
def gauss(V, c, s):
    d = V - _v(c)
    return np.exp(-np.sum(d * d, axis=1) / (2 * s * s))


def head_sdf(P, design):
    """Head + neck in head-local coordinates (origin between the eyes at skull centre)."""
    D = design
    d = ellipsoid(P, (0, 0.016, 0.03), (0.082, 0.093, 0.09))                    # cranium
    d = smin(d, ellipsoid(P, (0, -0.01, -0.02), (0.07, 0.079, 0.08)), 0.02)       # face
    d = smin(d, ellipsoid(P, (0, -0.03, -0.066), (0.05 * D["jaw"], 0.052, 0.042)), 0.022)
    d = smin(d, ellipsoid(P, (0, -0.061, -0.086), (0.023, 0.018, 0.02)), 0.012)  # chin
    for sx in (1, -1):
        d = smin(d, ellipsoid(P, (sx * 0.043, -0.054, -0.026), (0.028, 0.024, 0.026)), 0.016)   # cheeks
        d = smin(d, ellipsoid(P, (sx * 0.054, -0.04, -0.002), (0.02, 0.018, 0.014)), 0.012)     # cheekbones
        d = smin(d, capsule(P, (sx * 0.012, -0.077, 0.03), (sx * 0.05, -0.066, 0.032), 0.0105), 0.012)   # brow
        d = sub(d, ellipsoid(P, (sx * 0.033, -0.081, 0.003), (0.021, 0.016, 0.016)), 0.01)     # eye socket
    # nose
    d = smin(d, rcone(P, (0, -0.081, 0.016), (0, -0.097, -0.019), 0.0072, 0.0092), 0.008)
    d = smin(d, sphere(P, (0, -0.1005 - D["nose"], -0.0245), 0.0118 + D["nose"] * 0.4), 0.006)
    for sx in (1, -1):
        d = smin(d, sphere(P, (sx * 0.0132, -0.0905, -0.0295), 0.0082), 0.006)               # alae
        d = sub(d, sphere(P, (sx * 0.0064, -0.0985 - D["nose"] * 0.5, -0.0355), 0.0036), 0.003)   # nostrils
    # mouth
    d = smin(d, capsule(P, (-0.019, -0.0815, -0.0468), (0.019, -0.0815, -0.0468), 0.0038), 0.008)
    d = smin(d, capsule(P, (-0.0145, -0.0805, -0.0566), (0.0145, -0.0805, -0.0566), 0.0045), 0.008)
    smile = D["smile"]
    crease = polyline(P, [(-0.0255, -0.0795, -0.0488 + smile), (-0.012, -0.0865, -0.052), (0, -0.0885, -0.0525),
                          (0.012, -0.0865, -0.052), (0.0255, -0.0795, -0.0488 + smile)],
                      [0.0013, 0.0016, 0.0017, 0.0016, 0.0013])
    d = sub(d, crease, 0.0016)
    for sx in (1, -1):
        d = sub(d, sphere(P, (sx * 0.0255, -0.079, -0.0492 + smile), 0.0024), 0.003)         # corner dimples
    d = sub(d, capsule(P, (0, -0.0935, -0.0405), (0, -0.0905, -0.0335), 0.0022), 0.003)        # philtrum
    d = smin(d, rcone(P, (0, 0.012, -0.06), (0, 0.022, -0.17), 0.043, 0.047), 0.03)           # neck
    return d


def _left_ear(Q):
    R = rotz(-16) @ rotx(-10)
    c = (0.081, 0.018, -0.004)
    q = (Q - _v(c)) @ R
    e = ellipsoid(q, (0, 0, 0), (0.0095, 0.022, 0.031))
    e = sub(e, ellipsoid(q, (0.006, -0.002, -0.004), (0.0085, 0.0125, 0.017)), 0.003)      # concha
    e = smin(e, sphere(q, (0.001, 0.003, -0.028), 0.0088), 0.006)                          # lobe
    e = smin(e, sphere(q, (0.004, -0.014, -0.006), 0.0045), 0.003)                         # tragus
    return e


def ears_sdf(P):
    Q = P.copy()
    Q[:, 0] = np.abs(Q[:, 0])
    return _left_ear(Q)


def hand_sdf(P, sx):
    A, F, N = (_v(x) for x in SK.hand_frame(sx))
    W = _v(SK.mirror(SK.WR, sx))
    El = _v(SK.mirror(SK.EL, sx))
    R = np.stack([F, A, np.cross(F, A)], axis=1)
    d = ellipsoid(P, W + A * 0.046 - N * 0.002, (0.04, 0.047, 0.0155), R)                          # palm
    d = smin(d, ellipsoid(P, W + A * 0.03 + F * 0.021 + N * 0.006, (0.017, 0.022, 0.014), R), 0.008)   # thenar
    d = smin(d, ellipsoid(P, W + A * 0.055 - F * 0.022 + N * 0.003, (0.012, 0.025, 0.011), R), 0.008)
    d = smin(d, rcone(P, El + (W - El) * 0.02, W + A * 0.012, 0.037, 0.0265), 0.012)                 # forearm
    d = smin(d, ellipsoid(P, El + (W - El) * 0.3, (0.04, 0.04, 0.034),
                          rot_cols(np.cross(A, N), A, N)), 0.02)                                     # forearm muscle
    hp = SK.hand_points(sx)
    for fn, (pts, r) in hp.items():
        pts = [_v(p) for p in pts]
        if fn == "thumb":
            rr = [0.0128, 0.0108, 0.0095, 0.0088]
            for k in range(3):
                d = smin(d, rcone(P, pts[k], pts[k + 1], rr[k], rr[k + 1]), 0.006 if k == 0 else 0.002)
            continue
        rr = [r * 1.06, r * 0.95, r * 0.88, r * 0.8]
        f = None
        for k in range(3):
            seg = rcone(P, pts[k], pts[k + 1], rr[k], rr[k + 1])
            f = seg if f is None else smin(f, seg, 0.0015)
        f = smin(f, sphere(P, pts[0] - N * 0.002, r * 1.12), 0.003)                                  # knuckle
        d = smin(d, f, 0.0035)
    return d


def hand_attr(V, sx):
    """tint: R blush (knuckles, fingertips), G crease, B nails."""
    hp = SK.hand_points(sx)
    A, F, N = (_v(x) for x in SK.hand_frame(sx))
    r = np.zeros(len(V))
    g = np.zeros(len(V))
    b = np.zeros(len(V))
    for fn, (pts, rad) in hp.items():
        tip = _v(pts[3])
        r += gauss(V, tip, 0.009) * 0.6 + gauss(V, _v(pts[1]), 0.006) * 0.35
        # nail: dorsal side (opposite to the palm normal) near the tip
        nail_c = _v(pts[3]) - (_v(pts[3]) - _v(pts[2])) * 0.35 - N * rad * 0.75
        b += gauss(V, nail_c, rad * 0.55) * 1.4
    return np.stack([np.clip(r, 0, 1) * 0.8 + 0.18, g, np.clip(b, 0, 1)], axis=1)


def head_attr(V, design):
    av = V.copy()
    av[:, 0] = np.abs(av[:, 0])
    r = gauss(av, (0.044, -0.07, -0.03), 0.016) * 0.85 + gauss(V, (0, -0.108, -0.025), 0.01) * 0.6
    r += gauss(av, (0.03, -0.08, 0.035), 0.012) * 0.15
    g = (gauss(av, (0.033, -0.085, 0.017), 0.008) * 0.45 + gauss(av, (0.0064, -0.099, -0.036), 0.0035) * 1.0
         + gauss(av, (0.024, -0.082, -0.05), 0.003) * 0.6 + gauss(av, (0.016, -0.093, -0.022), 0.005) * 0.25)
    lip_up = gauss(V * [0.42, 1, 1], (0, -0.0895, -0.0468), 0.0058)
    lip_lo = gauss(V * [0.5, 1, 1], (0, -0.0875, -0.057), 0.0068)
    b = np.clip((lip_up + lip_lo) * 1.15, 0, 1) * (np.abs(V[:, 0]) < 0.026)
    r *= (V[:, 2] > -0.075)
    return np.stack([np.clip(r, 0, 1), np.clip(g, 0, 1), b], axis=1)


# ---- clothing
def torso_body(P, ease=0.0):
    d = ellipsoid(P, (0, 0.004, 1.03), (0.14 + ease, 0.098 + ease, 0.09))
    d = smin(d, ellipsoid(P, (0, 0.006, 1.21), (0.152 + ease, 0.104 + ease, 0.14)), 0.05)
    d = smin(d, ellipsoid(P, (0, 0.012, 1.315), (0.148 + ease, 0.09 + ease, 0.07)), 0.05)
    d = smin(d, ellipsoid(P, (0, 0.004, 0.94), (0.148 + ease, 0.102 + ease, 0.08)), 0.04)
    for sx in (1, -1):
        d = smin(d, sphere(P, SK.mirror((0.163, 0.008, 1.34), sx), 0.054 + ease), 0.045)
        d = smin(d, capsule(P, SK.mirror((0.05, 0.012, 1.385), sx), SK.mirror((0.15, 0.01, 1.36), sx), 0.038 + ease),
                 0.04)                                                                       # trapezius slope
    return d


def shirt_sdf(P):
    d = torso_body(P, 0.006)
    for sx in (1, -1):
        sh, el = _v(SK.mirror(SK.SH, sx)), _v(SK.mirror(SK.EL, sx))
        d = smin(d, rcone(P, sh, sh + (el - sh) * 0.8, 0.054, 0.047), 0.03)
        ax = (el - sh) / np.linalg.norm(el - sh)
        d = smin(d, torus(P, sh + (el - sh) * 0.8, ax, 0.046, 0.0105), 0.004)          # rolled cuff
        d = smin(d, torus(P, sh + (el - sh) * 0.86, ax, 0.044, 0.009), 0.004)
    d = sub(d, capsule(P, (0, 0.014, 1.38), (0, 0.016, 1.6), 0.05), 0.01)                 # neck hole
    d = smin(d, rbox(P, (0, -0.106, 1.17), (0.0145, 0.006, 0.2), rr=0.004), 0.004)        # placket
    d = d + wrinkles(P, 0.0028, 70.0, 3) * (P[:, 2] < 1.1) + wrinkles(P, 0.0015, 120.0, 4)
    return smax(d, plane(P, (0, 0, -1), -0.93), 0.0)


def collar_sdf(P):
    band = shell(capsule(P, (0, 0.014, 1.36), (0, 0.016, 1.44), 0.061), 0.0035)
    band = smax(band, plane(P, (0, 0, 1), 1.392), 0.0)
    band = smax(band, -plane(P, (0, 0, 1), 1.355), 0.0)
    band = sub(band, rbox(P, (0, -0.07, 1.42), (0.014, 0.03, 0.06)), 0.002)              # front opening
    Q = P.copy()
    Q[:, 0] = np.abs(Q[:, 0])
    flap = ellipsoid(Q, (0.036, -0.092, 1.368), (0.032, 0.022, 0.0032),
                     rot_cols((0.5, -0.28, -0.82), (0.86, 0.1, 0.5), (0, 0, 1)))
    return smin(band, flap, 0.004)


def vest_sdf(P):
    base = torso_body(P, 0.006)
    outer = base - 0.019
    inner = base - 0.009
    d = smax(outer, -inner, 0.0)
    d = smax(d, -plane(P, (0, 0, 1), 0.955), 0.0)                       # hem
    d = smax(d, plane(P, (0, 0, 1), 1.43), 0.0)
    for sx in (1, -1):
        d = sub(d, ellipsoid(P, SK.mirror((0.2, 0.008, 1.3), sx), (0.072, 0.09, 0.115)), 0.006)   # armholes
    # (a V-opening cut used to sit here; its half-space test selected y > -0.02, i.e. the BACK of the vest,
    #  leaving the back cut open. The vest is closed front and back; the neck capsule below shapes the collar.)
    d = sub(d, capsule(P, (0, 0.014, 1.38), (0, 0.016, 1.6), 0.07), 0.006)
    # pockets with flaps (raised panels)
    for sx in (1, -1):
        for (px, pz, hw, hh) in ((0.072, 1.235, 0.032, 0.03), (0.082, 1.045, 0.038, 0.036)):
            c = (sx * px, -0.108 if pz > 1.1 else -0.104, pz)
            d = smin(d, rbox(P, c, (hw, 0.012, hh), rr=0.006), 0.003)
            d = smin(d, rbox(P, (c[0], c[1] - 0.004, pz + hh * 0.82), (hw + 0.003, 0.01, hh * 0.32), rr=0.005), 0.002)
    return d + wrinkles(P, 0.0018, 60.0, 7)


def trousers_sdf(P):
    d = ellipsoid(P, (0, 0.006, 0.935), (0.148, 0.103, 0.1))
    d = smin(d, ellipsoid(P, (0, 0.004, 1.0), (0.143, 0.099, 0.05)), 0.02)
    for sx in (1, -1):
        hip, knee, ank = (_v(SK.mirror(x, sx)) for x in (SK.HIP, SK.KNEE, SK.ANK))
        d = smin(d, rcone(P, hip, knee, 0.081, 0.064), 0.035)
        d = smin(d, rcone(P, knee, ank + _v((0, 0, 0.07)), 0.063, 0.06), 0.015)
        d = smin(d, sphere(P, knee + _v((0, -0.006, 0)), 0.066), 0.02)
        d = smin(d, torus(P, ank + _v((0, 0, 0.075)), (0, 0, 1), 0.06, 0.012), 0.006)      # cuff
        pk = hip + (knee - hip) * 0.42 + _v((sx * 0.07, -0.005, 0))
        d = smin(d, rbox(P, pk, (0.014, 0.045, 0.055), rr=0.01), 0.008)                     # cargo pocket
        d = smin(d, rbox(P, pk + _v((sx * 0.004, 0, 0.05)), (0.012, 0.048, 0.016), rr=0.006), 0.003)   # flap
    d = smax(d, plane(P, (0, 0, 1), 1.012), 0.0)
    d = smax(d, -plane(P, (0, 0, 1), ANK_CUT), 0.0)
    knees = np.zeros(len(P))
    for sx in (1, -1):
        knees += gauss(P, SK.mirror(SK.KNEE, sx), 0.08) + gauss(P, SK.mirror((0.1, 0.01, 0.2), sx), 0.07)
    return d + wrinkles(P, 0.004, 80.0, 11) * np.clip(knees, 0, 1) + wrinkles(P, 0.0012, 140.0, 12)


ANK_CUT = 0.15


def belt_sdf(P):
    e = ellipsoid(P, (0, 0.004, 1.0), (0.149, 0.107, 0.5))
    d = smax(shell(e, 0.004), np.abs(P[:, 2] - 1.0) - 0.016, 0.0)
    return d


def boot_sdf(P, sx):
    x = sx * 0.1
    d = ellipsoid(P, (x, 0.022, 0.052), (0.047, 0.05, 0.052))
    d = smin(d, ellipsoid(P, (x, -0.068, 0.045), (0.053, 0.068, 0.045)), 0.03)
    d = smin(d, ellipsoid(P, (x, -0.118, 0.043), (0.046, 0.04, 0.04)), 0.02)
    d = smin(d, rcone(P, (x, 0.014, 0.06), (x, 0.014, 0.178), 0.057, 0.06), 0.03)
    d = smin(d, torus(P, (x, 0.014, 0.178), (0, 0, 1), 0.058, 0.009), 0.006)            # padded collar
    d = smin(d, rbox(P, (x, -0.06, 0.105), (0.024, 0.04, 0.05), rx(-35), rr=0.012), 0.012)   # tongue
    d = smax(d, -plane(P, (0, 0, 1), 0.024), 0.0)
    return d + wrinkles(P, 0.0012, 150.0, 21)


def rx(deg):
    return rotx(deg)


def sole_sdf(P, sx):
    Q = P.copy()
    Q[:, 2] = 0.045
    foot = boot_sdf(Q, sx) - 0.0035
    d = smax(foot, np.abs(P[:, 2] - 0.0135) - 0.0135, 0.004)
    grooves = np.abs(np.sin(P[:, 1] * 260.0)) * 0.0025
    return d + np.where(P[:, 2] < 0.006, grooves, 0.0)


def hair_sdf(P, style, head_d):
    """Hair mass under a hat: an offset shell of the skull with curly lobes along the hemline."""
    if style == "curly":
        mass = head_d - 0.011
        back = np.clip(P[:, 1] / 0.04, 0, 1)
        region = np.maximum(-(P[:, 2] + 0.035 + 0.025 * back), P[:, 2] - 0.085)
        keep = np.minimum(-(P[:, 1] + 0.035), -(P[:, 2] - 0.05))   # no hair on the face below the hat
        d = smax(mass, region, 0.01)
        d = smax(d, keep, 0.012)
        rng = np.random.default_rng(5)
        for i in range(70):
            a = rng.uniform(-2.35, 2.35)
            z = rng.uniform(-0.04, 0.035)
            rr = 0.0835 + 0.006 * rng.random()
            c = (math.sin(a) * rr, math.cos(a) * rr * 1.1 + 0.014, z - 0.012 * (abs(a) < 1.2))
            if c[1] < -0.03:
                continue
            d = smin(d, sphere(P, c, rng.uniform(0.0085, 0.0135)), 0.005)
        for i in range(6):   # fringe curls peeking under the brim
            x = -0.05 + i * 0.02
            d = smin(d, ellipsoid(P, (x, -0.074 + abs(x) * 0.25, 0.064 - abs(x) * 0.1), (0.012, 0.01, 0.011)), 0.005)
        # ears stay clear
        for sx in (1, -1):
            d = sub(d, ellipsoid(P, (sx * 0.085, 0.016, -0.004), (0.02, 0.028, 0.036)), 0.004)
        return d
    if style == "short":
        mass = head_d - 0.007
        back = np.clip(P[:, 1] / 0.04, 0, 1)
        region = -(P[:, 2] + 0.02 + 0.03 * back)
        d = smax(mass, region, 0.008)
        keep = np.minimum(-(P[:, 1] + 0.045), -(P[:, 2] - 0.055))
        d = smax(d, keep, 0.01)
        for sx in (1, -1):
            d = sub(d, ellipsoid(P, (sx * 0.085, 0.016, -0.004), (0.02, 0.028, 0.036)), 0.004)
        return d + wrinkles(P, 0.0015, 300.0, 9)
    raise ValueError(style)


def mustache_sdf(P):
    return polyline(P, [(-0.026, -0.083, -0.045), (-0.012, -0.095, -0.0405), (0, -0.098, -0.0395),
                        (0.012, -0.095, -0.0405), (0.026, -0.083, -0.045)], [0.004, 0.0062, 0.006, 0.0062, 0.004])


def scarf_sdf(P):
    R = np.array([[1, 0, 0], [0, 0.17, 1], [0, 1, -0.17]]).T * 0 + rot_cols((1, 0, 0), (0, 1, -0.2), (0, 0.2, 1))
    q = (P - _v((0, 0.02, 1.405))) @ R
    d = ellipsoid(q, (0, 0, 0), (0.077, 0.072, 0.022))
    d = sub(d, ellipsoid(q, (0, 0, 0), (0.058, 0.054, 0.05)), 0.006)                 # ring around the neck
    d = smin(d, ellipsoid(P, (0.03, -0.068, 1.392), (0.017, 0.012, 0.015)), 0.006)   # knot
    d = smin(d, ellipsoid(P, (0.045, -0.07, 1.352), (0.014, 0.0055, 0.034), roty(-22)), 0.005)
    d = smin(d, ellipsoid(P, (0.02, -0.073, 1.355), (0.012, 0.0055, 0.03), roty(10)), 0.005)
    return d + wrinkles(P, 0.0012, 220.0, 31)


def satchel_sdf(P):
    d = rbox(P, (-0.178, -0.015, 0.93), (0.028, 0.105, 0.082), rr=0.022)
    flap = rbox(P, (-0.2, -0.015, 0.965), (0.006, 0.108, 0.052), rr=0.005)
    return smin(d, flap, 0.004) + wrinkles(P, 0.0015, 120.0, 41)


DESIGNS = {
    "pip": dict(jaw=1.0, nose=0.0, smile=0.0028, hair="curly"),
    "farmer": dict(jaw=1.12, nose=0.003, smile=0.0012, hair="short"),
    "researcher": dict(jaw=0.96, nose=0.0015, smile=0.002, hair="short"),
}


def build_human(out, kind):
    import json
    D = DESIGNS[kind]
    os.makedirs(out, exist_ok=True)
    MANIFEST.clear()
    print(kind, flush=True)
    HC = SK.HEAD_C
    S = SK.HEAD_S
    hf0 = lambda P: head_sdf(P, D)   # noqa: E731
    hf = lambda P: head_sdf(P / S, D) * S   # noqa: E731
    bb = lambda lo, hi: (_v(lo) * S, _v(hi) * S)   # noqa: E731
    mesh(os.path.join(out, "head.bin"), hf, *bb((-0.1, -0.13, -0.19), (0.1, 0.12, 0.14)), 0.0019 * S, smooth=5,
         attr_fn=lambda V: head_attr(V / S, D), bones=("head", "neck", "chest"), power=3.0, eps=0.03, mat="skin",
         local=HC)
    mesh(os.path.join(out, "ears.bin"), lambda P: ears_sdf(P / S) * S, *bb((-0.1, -0.02, -0.05), (0.1, 0.05, 0.04)),
         0.0013 * S, smooth=4, attr_fn=lambda V: np.tile([0.55, 0.0, 0.0], (len(V), 1)), mat="skin", local=HC)
    mesh(os.path.join(out, "hair.bin"), lambda P: hair_sdf(P / S, D["hair"], hf0(P / S)) * S,
         *bb((-0.11, -0.11, -0.07), (0.11, 0.13, 0.13)), 0.0021 * S, smooth=5, mat="hair", local=HC)
    if kind == "farmer":
        mesh(os.path.join(out, "mustache.bin"), lambda P: mustache_sdf(P / S) * S,
             *bb((-0.04, -0.11, -0.06), (0.04, -0.07, -0.03)), 0.0012 * S, 3, mat="hair", local=HC)
    fing = lambda s: [f"{f}{k}.{s}" for f in ("index", "middle", "ring", "pinky", "thumb") for k in (1, 2)]  # noqa
    for sx, s in ((1, "L"), (-1, "R")):
        lo = np.minimum(_v(SK.mirror(SK.EL, sx)), _v(SK.mirror(SK.WR, sx))) - 0.06
        hi = np.maximum(_v(SK.mirror(SK.EL, sx)), _v(SK.mirror(SK.WR, sx))) + 0.06
        lo[2] = 0.66
        mesh(os.path.join(out, f"arm{s}.bin"), lambda P, sx=sx: hand_sdf(P, sx), lo, hi, 0.0016, smooth=4,
             attr_fn=lambda V, sx=sx: hand_attr(V, sx), mat="skin",
             bones=[f"upperarm.{s}", f"forearm.{s}", f"hand.{s}"] + fing(s), power=6.0, eps=0.002)
        mesh(os.path.join(out, f"boot{s}.bin"), lambda P, sx=sx: boot_sdf(P, sx), (sx * 0.1 - 0.08, -0.2, 0.0),
             (sx * 0.1 + 0.08, 0.1, 0.2), 0.0028, smooth=5, mat="boot", bones=[f"shin.{s}", f"foot.{s}", f"toe.{s}"],
             power=5.0)
        mesh(os.path.join(out, f"sole{s}.bin"), lambda P, sx=sx: sole_sdf(P, sx), (sx * 0.1 - 0.075, -0.18, -0.01),
             (sx * 0.1 + 0.075, 0.1, 0.04), 0.0022, smooth=2, mat="sole", bones=[f"foot.{s}", f"toe.{s}"], power=5.0)
    torso = ["pelvis", "spine", "chest", "neck", "shoulder.L", "shoulder.R", "upperarm.L", "upperarm.R"]
    mesh(os.path.join(out, "shirt.bin"), shirt_sdf, (-0.33, -0.15, 0.9), (0.33, 0.15, 1.47), 0.0034, smooth=6,
         mat="shirt", bones="shirt", eps=0.03)
    mesh(os.path.join(out, "collar.bin"), collar_sdf, (-0.09, -0.13, 1.32), (0.09, 0.1, 1.46), 0.0016, smooth=3,
         mat="shirt", bones=("chest", "neck"))
    if kind in ("pip", "researcher"):
        mesh(os.path.join(out, "vest.bin"), vest_sdf, (-0.22, -0.15, 0.94), (0.22, 0.15, 1.45), 0.0032, smooth=4,
             mat="vest", bones=("pelvis", "spine", "chest", "shoulder.L", "shoulder.R"), eps=0.03)
    mesh(os.path.join(out, "trousers.bin"), trousers_sdf, (-0.25, -0.13, 0.12), (0.25, 0.14, 1.03), 0.0042, smooth=6,
         mat="trousers", bones=("pelvis", "spine", "thigh.L", "thigh.R", "shin.L", "shin.R"), eps=0.03)
    mesh(os.path.join(out, "belt.bin"), belt_sdf, (-0.18, -0.13, 0.97), (0.18, 0.13, 1.03), 0.0018, smooth=2,
         mat="belt", bones=("pelvis", "spine"))
    if kind == "pip":
        mesh(os.path.join(out, "scarf.bin"), scarf_sdf, (-0.1, -0.11, 1.3), (0.1, 0.11, 1.46), 0.0018, smooth=3,
             mat="scarf", bones=("chest", "neck"))
        mesh(os.path.join(out, "satchel.bin"), satchel_sdf, (-0.23, -0.14, 0.83), (-0.13, 0.11, 1.03), 0.0025, 3,
             mat="satchel", bones=("pelvis",))
    json.dump(dict(kind=kind, parts=MANIFEST, bones=[b[0] for b in SK.bones()]),
              open(os.path.join(out, "manifest.json"), "w"), indent=1)



# ------------------------------------------------------------------ bats
import batskel as BK  # noqa: E402


def _bat_ear(Q, sp):
    """Left ear (x>0) on mirrored coordinates."""
    S = BK.SPECIES[sp]
    w, h, flare = S["ear"]
    R = rotz(-20) @ roty(-flare) @ rotx(-12)
    c = _v((0.0072, -0.032, 0.016)) + _v((0.002, 0.0, 0.0)) * (flare / 30.0)
    q = (Q - c) @ R
    e = ellipsoid(q, (0, 0, h * 0.55), (0.0018, w * 0.5, h * 0.62))
    e = sub(e, ellipsoid(q, (-0.0016, 0, h * 0.58), (0.0015, w * 0.4, h * 0.52)), 0.0006)     # concha (front)
    if sp in ("myotis", "freetail"):
        e = smin(e, rcone(q, (-0.0006, -w * 0.18, h * 0.12), (-0.0008, -w * 0.2, h * 0.5), 0.0011, 0.0004), 0.0005)
    for k in range(4):   # ridges across the ear
        e = smin(e, capsule(q, (-0.0006, -w * 0.3, h * (0.3 + 0.15 * k)), (-0.0006, w * 0.3, h * (0.32 + 0.15 * k)),
                            0.00045), 0.0004)
    return e


def bat_body_sdf(P, sp):
    S = BK.SPECIES[sp]
    sn = S["snout"]
    d = ellipsoid(P, (0, 0.002, 0.0), (0.0155, 0.029, 0.0135))                          # torso
    d = smin(d, ellipsoid(P, (0, -0.016, 0.002), (0.0165, 0.014, 0.0135)), 0.006)       # chest / shoulders
    d = smin(d, ellipsoid(P, (0, -0.036, 0.007), (0.0122, 0.0135, 0.0112)), 0.006)      # head
    d = smin(d, ellipsoid(P, (0, -0.032, 0.0115), (0.0105, 0.011, 0.0085)), 0.004)     # crown
    d = smin(d, rcone(P, (0, -0.043, 0.005), (0, -0.046 - sn, 0.0028), 0.0058, 0.0028), 0.004)   # snout (tapered)
    d = smin(d, ellipsoid(P, (0, -0.0462 - sn, 0.0034), (0.0027, 0.0018, 0.0021)), 0.0012)          # nose pad
    for sx in (1, -1):
        d = sub(d, sphere(P, (sx * 0.0013, -0.0488 - sn, 0.0038), 0.0008), 0.0005)    # nostrils
        d = smin(d, ellipsoid(P, (sx * 0.0042, -0.0425 - sn * 0.6, 0.0012), (0.0028, 0.006 + sn * 0.3, 0.0026)),
                 0.0025)                                                               # lips
        d = sub(d, capsule(P, (sx * 0.004, -0.046 - sn * 0.9, -0.0005), (sx * 0.0085, -0.04, 0.0), 0.0006), 0.0005)
        d = sub(d, sphere(P, (sx * 0.0062, -0.0445 - sn * 0.25, 0.0088), 0.0018), 0.001)   # eye socket
    if S.get("wrinkled"):
        lip = sphere(P, (0, -0.048 - sn, 0.0), 0.0058)
        d = smin(d, lip + np.abs(np.sin(P[:, 0] * 2200.0)) * 0.0005, 0.002)
    if S["nose_leaf"]:
        d = smin(d, ellipsoid(P, (0, -0.0475 - sn, 0.0065), (0.0022, 0.0009, 0.0034), rotx(-15)), 0.0007)
    Q = P.copy()
    Q[:, 0] = np.abs(Q[:, 0])
    d = smin(d, _bat_ear(Q, sp), 0.0012)
    # legs + feet + claws
    for sx in (1, -1):
        H, Kn, A = (_v(BK.mirror(BK.points(sp)[k], sx)) for k in ("H", "Kn", "A"))
        d = smin(d, rcone(P, H, Kn, 0.0034, 0.0019), 0.003)
        d = smin(d, rcone(P, Kn, A, 0.0018, 0.0014), 0.001)
        d = smin(d, ellipsoid(P, A + _v((0, 0.003, -0.0005)), (0.0024, 0.0032, 0.0011)), 0.001)
        for k in range(5):
            t0 = A + _v((sx * (-0.0018 + k * 0.0009), 0.0055, -0.0006))
            d = smin(d, rcone(P, t0, t0 + _v((0, 0.0028, -0.0016)), 0.00055, 0.0002), 0.0003)
    if S["tail"] > 0:
        P0 = _v(BK.points(sp)["tail0"])
        P1 = _v(BK.points(sp)["tail1"])
        d = smin(d, rcone(P, P0, P1, 0.0022, 0.0007), 0.003)
    return d


def bat_attr(V, sp):
    """R = fur density, G = bare-skin darkness, B = white-nose fungus mask (muzzle, ears)."""
    S = BK.SPECIES[sp]
    sn = S["snout"]
    face = gauss(V, (0, -0.046 - sn * 0.6, 0.003), 0.006 + sn * 0.4)
    Q = V.copy()
    Q[:, 0] = np.abs(Q[:, 0])
    ear = np.clip((V[:, 2] - 0.013) / 0.004, 0, 1) * (np.abs(V[:, 0]) > 0.004)
    legs = np.clip((V[:, 1] - 0.03) / 0.006, 0, 1)
    tail = np.clip((V[:, 1] - 0.03) / 0.01, 0, 1) * (np.abs(V[:, 0]) < 0.004)
    fur = np.clip(1.0 - face * 1.6 - ear - legs * 0.9 - tail, 0, 1)
    skin = np.clip(face * 1.3 + ear + legs + tail, 0, 1)
    fungus = np.clip(gauss(V, (0, -0.047 - sn, 0.004), 0.0065) * 1.4 + ear * 0.6, 0, 1)
    return np.stack([fur, skin, fungus], axis=1)


def _hang_ear(Q, sp):
    w, h, flare = BK.SPECIES[sp]["ear"]
    R = roty(-28) @ rotx(-18)
    c = _v((0.0085, -0.002, -0.036))
    q = (Q - c) @ R
    e = ellipsoid(q, (0, 0, -h * 0.55), (0.0016, w * 0.48, h * 0.6))
    e = sub(e, ellipsoid(q, (0, -0.0014, -h * 0.58), (0.0014, w * 0.38, h * 0.5)), 0.0005)
    if sp in ("myotis", "freetail"):
        e = smin(e, rcone(q, (0, -0.0008, -h * 0.15), (0, -0.001, -h * 0.5), 0.001, 0.0004), 0.0005)   # tragus
    return e


def bat_hanger_sdf(P, sp):
    """Hibernating / roosting bat hanging head-down, wings folded like a cape (feet at +Z, face at -Z)."""
    S = BK.SPECIES[sp]
    sn = S["snout"]
    d = ellipsoid(P, (0, 0.0, 0.0), (0.0142, 0.0125, 0.022))                                # body
    d = smin(d, ellipsoid(P, (0, -0.0035, -0.026), (0.0118, 0.0112, 0.0115)), 0.006)       # head
    d = smin(d, rcone(P, (0, -0.0095, -0.031), (0, -0.0125 - sn * 0.5, -0.039 - sn * 0.5), 0.0055, 0.0028), 0.003)
    d = smin(d, ellipsoid(P, (0, -0.0135 - sn * 0.5, -0.0405 - sn * 0.5), (0.0026, 0.0018, 0.0021)), 0.0012)
    for sx in (1, -1):
        d = sub(d, sphere(P, (sx * 0.0011, -0.0148 - sn * 0.5, -0.0415 - sn * 0.5), 0.0006), 0.0004)   # nostrils
        d = smin(d, ellipsoid(P, (sx * 0.0037, -0.0105 - sn * 0.3, -0.037 - sn * 0.4), (0.0025, 0.003, 0.0045)),
                 0.002)                                                                               # lips
        d = sub(d, sphere(P, (sx * 0.0058, -0.0105, -0.0265), 0.0015), 0.0008)                         # eye socket
        # folded wing: leathery cape over the side, forearm ridge, thumb claw near the chin
        wrap = ellipsoid(P, (sx * 0.0102, -0.0012, -0.002), (0.0072, 0.0128, 0.023))
        d = smin(d, wrap, 0.003)
        el, wr = _v((sx * 0.0145, 0.0005, 0.016)), _v((sx * 0.0112, -0.0085, -0.02))
        d = smin(d, rcone(P, el, wr, 0.0022, 0.0018), 0.0015)
        d = smin(d, rcone(P, wr, wr + _v((sx * -0.0012, -0.0035, -0.004)), 0.0011, 0.0003), 0.0005)
        # feet gripping at the top
        d = smin(d, rcone(P, (sx * 0.0055, 0.001, 0.02), (sx * 0.0045, 0.0, 0.032), 0.0021, 0.0013), 0.002)
        for k in range(3):
            t0 = _v((sx * (0.003 + k * 0.0011), 0.0, 0.033))
            d = smin(d, rcone(P, t0, t0 + _v((0, -0.0026, 0.0013)), 0.00045, 0.00018), 0.0003)
    Q = P.copy()
    Q[:, 0] = np.abs(Q[:, 0])
    d = smin(d, _hang_ear(Q, sp), 0.0012)
    return d + wrinkles(P, 0.00025, 1600.0, 51)


def bat_hanger_attr(V, sp):
    sn = BK.SPECIES[sp]["snout"]
    face = gauss(V, (0, -0.0125 - sn * 0.5, -0.039 - sn * 0.5), 0.0055 + sn * 0.3)
    side = np.clip((np.abs(V[:, 0]) - 0.0098) / 0.0025, 0, 1) * (V[:, 2] < 0.024) * (V[:, 2] > -0.026)
    ear = np.clip((-V[:, 2] - 0.036) / 0.003, 0, 1) * (np.abs(V[:, 0]) > 0.006)
    feet = np.clip((V[:, 2] - 0.022) / 0.003, 0, 1)
    fur = np.clip(1 - face * 1.5 - side - ear - feet, 0, 1)
    skin = np.clip(face * 1.2 + side + ear + feet, 0, 1)
    fungus = np.clip(face * 1.6 + ear * 0.8 + side * gauss(V, (0, -0.008, -0.015), 0.012) * 1.1, 0, 1)
    return np.stack([fur, skin, fungus], axis=1)


def build_bat(out, sp):
    import json
    os.makedirs(out, exist_ok=True)
    print("bat", sp, flush=True)
    MANIFEST.clear()
    V, F = surface_nets(lambda P: bat_body_sdf(P, sp), (-0.03, -0.075, -0.02), (0.03, 0.1, 0.04), 0.00042)
    V = taubin(V, F, 4)
    write(os.path.join(out, "body.bin"), V, F, bat_attr(V, sp))
    V, F = surface_nets(lambda P: bat_hanger_sdf(P, sp), (-0.03, -0.035, -0.07), (0.03, 0.025, 0.045), 0.0004)
    V = taubin(V, F, 4)
    write(os.path.join(out, "hanger.bin"), V, F, bat_hanger_attr(V, sp))
    json.dump(dict(species=sp), open(os.path.join(out, "manifest.json"), "w"))


# ------------------------------------------------------------------ environment rock meshes
_PERM = np.random.default_rng(1234).permutation(256)
_PERM = np.concatenate([_PERM, _PERM])
_VALS = np.random.default_rng(99).uniform(-1, 1, 256)


def vnoise(P):
    """3D value noise in [-1, 1] (trilinear, smoothstep)."""
    i = np.floor(P).astype(np.int64)
    f = P - i
    u = f * f * (3 - 2 * f)
    i &= 255

    def h(dx, dy, dz):
        return _VALS[_PERM[_PERM[_PERM[(i[:, 0] + dx) & 255] + ((i[:, 1] + dy) & 255)] + ((i[:, 2] + dz) & 255)]]
    x0 = h(0, 0, 0) * (1 - u[:, 0]) + h(1, 0, 0) * u[:, 0]
    x1 = h(0, 1, 0) * (1 - u[:, 0]) + h(1, 1, 0) * u[:, 0]
    x2 = h(0, 0, 1) * (1 - u[:, 0]) + h(1, 0, 1) * u[:, 0]
    x3 = h(0, 1, 1) * (1 - u[:, 0]) + h(1, 1, 1) * u[:, 0]
    y0 = x0 * (1 - u[:, 1]) + x1 * u[:, 1]
    y1 = x2 * (1 - u[:, 1]) + x3 * u[:, 1]
    return y0 * (1 - u[:, 2]) + y1 * u[:, 2]


def fbm(P, freq, octaves=4, gain=0.5):
    a, s = 1.0, 0.0
    for o in range(octaves):
        s += a * vnoise(P * freq * (2 ** o) + o * 17.3)
        a *= gain
    return s


def cave_mouth_sdf(P):
    """Limestone cliff (vertical face toward -Y) with a large cave mouth at its foot; floor at z=0."""
    d = rbox(P, (0, 8.0, 3.2), (17.0, 7.0, 4.6), rr=2.6)
    d = smin(d, rbox(P, (-12.0, 5.5, 2.0), (6.0, 5.0, 3.5), rr=2.4), 1.5)
    d = smin(d, rbox(P, (12.0, 6.0, 2.4), (6.5, 5.5, 3.8), rr=2.4), 1.5)
    ledges = 0.35 * np.clip(np.sin(P[:, 2] * 2.6 + fbm(P, 0.25, 2) * 1.5), -0.2, 1.0)    # stepped strata
    d = d + ledges + fbm(P, 0.3, 4) * 1.1 + fbm(P, 2.0, 3) * 0.14
    mouth = ellipsoid(P, (0.0, 1.0, 1.4), (5.8, 4.2, 3.6))
    tunnel = rcone(P, (0.0, 1.5, 1.0), (0.0, 11.0, -3.0), 3.8, 2.6)
    hole = smin(mouth, tunnel, 1.0) + fbm(P, 0.8, 3) * 0.4
    d = sub(d, hole, 0.6)
    return smax(d, -(P[:, 2] + 1.5), 0.3)


def hibernaculum_sdf(P):
    """Cave chamber (inside-out: solid rock outside the cavity). Floor ~0, ceiling ~4 m.
    A passage leads to a daylight entrance at +Y."""
    cav = ellipsoid(P, (0, 0, 1.8), (6.5, 4.8, 2.6))
    cav = smin(cav, ellipsoid(P, (-3.5, -1.5, 1.4), (4.0, 3.5, 2.2)), 1.2)
    cav = smin(cav, ellipsoid(P, (3.8, 1.0, 1.6), (3.6, 3.2, 2.3)), 1.2)
    cav = smin(cav, rcone(P, (1.5, 3.0, 1.2), (3.5, 11.0, 1.6), 1.7, 2.0), 1.0)       # passage to the entrance
    cav = smax(cav, -(P[:, 2] - 0.0 - 0.15 * fbm(P, 0.6, 2)), 0.4)                    # flat-ish floor
    rock = -cav
    rock = rock + fbm(P, 0.45, 4) * 0.45 + fbm(P, 3.0, 3) * 0.06 + 0.06 * np.sin(P[:, 2] * 7.0)
    # flowstone columns and draperies
    for c, r in (((-4.5, -3.6, 1.5), 0.55), ((5.4, -1.8, 1.7), 0.45), ((-1.0, 3.6, 1.6), 0.4)):
        rock = smin(rock, rcone(P, (c[0], c[1], -0.5), (c[0] + 0.2, c[1], 4.6), r * 1.5, r * 0.8) +
                    0.08 * np.sin(np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0]) * 9.0), 0.6)
    rock = smax(rock, plane(P, (0, 1, 0), 10.5), 0.0)                                  # open end (entrance)
    return rock


def build_env(out):
    os.makedirs(out, exist_ok=True)
    V, F = surface_nets(cave_mouth_sdf, (-22, -6, -2), (22, 14, 9), 0.11)
    V = taubin(V, F, 4)
    write(os.path.join(out, "cave_mouth.bin"), V, F)
    V, F = surface_nets(hibernaculum_sdf, (-8.5, -6.8, -0.8), (8.0, 10.6, 5.2), 0.055)
    V = taubin(V, F, 4)
    write(os.path.join(out, "hibernaculum.bin"), V, F)


if __name__ == "__main__":
    out = sys.argv[1]
    for k in sys.argv[2].split(","):
        if k.startswith("bat_"):
            build_bat(os.path.join(out, k), k[4:])
        elif k == "env":
            build_env(os.path.join(out, "env"))
        else:
            build_human(os.path.join(out, k), k)
