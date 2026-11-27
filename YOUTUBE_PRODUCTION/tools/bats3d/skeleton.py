"""Shared skeleton for v3 humans (pure Python: used by the numpy SDF modeller and by Blender).

Metres, Z up, character faces -Y. Rest pose: relaxed A-pose, palms facing the thighs.
"""
import math

HEAD_C = (0.0, 0.006, 1.552)       # head-local origin (between the eyes, centre of the skull)
HEAD_S = 1.13                      # stylised head scale (bigger head = more appeal)


def v_add(a, b, s=1.0):
    return tuple(x + y * s for x, y in zip(a, b))


def v_sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def v_len(a):
    return math.sqrt(sum(x * x for x in a))


def v_norm(a):
    L = v_len(a) or 1.0
    return tuple(x / L for x in a)


def v_cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def v_dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def mirror(p, sx):
    return (p[0] * sx, p[1], p[2])


# left side (+x); right side mirrors
SH = (0.178, 0.008, 1.372)          # shoulder joint
EL = (0.252, 0.03, 1.118)           # elbow
WR = (0.302, 0.004, 0.888)          # wrist
HIP = (0.094, 0.004, 0.885)
KNEE = (0.1, -0.012, 0.475)
ANK = (0.1, 0.014, 0.088)
BALL = (0.1, -0.088, 0.03)
TOE = (0.1, -0.158, 0.026)


def hand_frame(sx):
    """(A along hand, F toward thumb/front, N palm normal pointing at the thigh) for side sx."""
    wr, el = mirror(WR, sx), mirror(EL, sx)
    A = v_norm(v_sub(wr, el))
    F = (0.0, -1.0, 0.0)
    F = v_norm(v_sub(F, tuple(a * v_dot(F, A) for a in A)))
    N = v_cross(A, F)
    if N[0] * sx > 0:
        N = tuple(-x for x in N)
    return A, F, N


FINGERS = [  # name, offset across knuckles (toward thumb +), segment lengths, base radius
    ("index", 0.0215, (0.036, 0.024, 0.02), 0.0088),
    ("middle", 0.0072, (0.041, 0.027, 0.021), 0.0091),
    ("ring", -0.0075, (0.038, 0.025, 0.02), 0.0086),
    ("pinky", -0.0215, (0.029, 0.02, 0.017), 0.0076),
]
PALM_LEN = 0.088


def hand_points(sx, curl=0.5):
    """Joint chains for fingers and thumb in the rest pose (relaxed curl)."""
    A, F, N = hand_frame(sx)
    W = mirror(WR, sx)

    def P(u, v, w):
        return tuple(W[i] + A[i] * u + F[i] * v + N[i] * w for i in range(3))
    out = {}
    for fn, off, segs, r in FINGERS:
        base = P(PALM_LEN - (0.007 if fn == "pinky" else 0.0) + (0.003 if fn == "middle" else 0.0), off, 0.0)
        pts = [base]
        d = A
        p = base
        spread = {"index": 0.03, "middle": 0.0, "ring": -0.025, "pinky": -0.06}[fn]
        for k, L in enumerate(segs):
            ang = math.radians(10 + 40 * curl) * (k + 1) * 0.6
            d = v_norm(tuple(A[i] * math.cos(ang) + N[i] * math.sin(ang) + F[i] * spread for i in range(3)))
            p = tuple(p[i] + d[i] * L for i in range(3))
            pts.append(p)
        out[fn] = (pts, r)
    t0 = P(0.016, 0.022, 0.004)
    t1 = P(0.047, 0.042, 0.014)
    d2 = v_norm(tuple(A[i] * 0.72 + F[i] * 0.42 + N[i] * 0.48 for i in range(3)))
    t2 = tuple(t1[i] + d2[i] * 0.031 for i in range(3))
    d3 = v_norm(tuple(A[i] * 0.8 + F[i] * 0.2 + N[i] * 0.58 for i in range(3)))
    t3 = tuple(t2[i] + d3[i] * 0.025 for i in range(3))
    out["thumb"] = ([t0, t1, t2, t3], 0.0105)
    return out


def bones():
    """Armature spec: (name, head, tail, parent)."""
    b = [("pelvis", (0, 0.004, 0.92), (0, 0.004, 1.02), None),
         ("spine", (0, 0.004, 1.02), (0, 0.004, 1.18), "pelvis"),
         ("chest", (0, 0.004, 1.18), (0, 0.006, 1.37), "spine"),
         ("neck", (0, 0.014, 1.395), (0, 0.016, 1.47), "chest"),
         ("head", (0, 0.016, 1.47), (0, 0.016, 1.69), "neck")]
    for sx, s in ((1, "L"), (-1, "R")):
        sh, el, wr = mirror(SH, sx), mirror(EL, sx), mirror(WR, sx)
        A, F, N = hand_frame(sx)
        b += [(f"shoulder.{s}", (sx * 0.03, 0.004, 1.375), sh, "chest"),
              (f"upperarm.{s}", sh, el, f"shoulder.{s}"),
              (f"forearm.{s}", el, wr, f"upperarm.{s}"),
              (f"hand.{s}", wr, tuple(wr[i] + A[i] * PALM_LEN for i in range(3)), f"forearm.{s}")]
        for fn, (pts, r) in hand_points(sx).items():
            b += [(f"{fn}1.{s}", pts[0], pts[1], f"hand.{s}"), (f"{fn}2.{s}", pts[1], pts[3], f"{fn}1.{s}")]
        b += [(f"thigh.{s}", mirror(HIP, sx), mirror(KNEE, sx), "pelvis"),
              (f"shin.{s}", mirror(KNEE, sx), mirror(ANK, sx), f"thigh.{s}"),
              (f"foot.{s}", mirror(ANK, sx), mirror(BALL, sx), f"shin.{s}"),
              (f"toe.{s}", mirror(BALL, sx), mirror(TOE, sx), f"foot.{s}")]
    return b
