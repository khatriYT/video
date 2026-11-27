"""Bat skeletons per species (pure Python; shared by sdf.py and bat.py).

Canonical frame: the bat faces -Y, up is +Z, the left wing extends toward +X. Wings are modelled fully
spread (flight rest pose). Units are metres for a little brown bat; other species carry a scale.
"""

SPECIES = {
    # name: scale, digit-tip overrides, tail, snout, ears, colours
    "myotis": dict(scale=1.0, d3tip=(0.142, -0.04), d4tip=(0.122, 0.014), d5tip=(0.097, 0.04), fore=1.0,
                   tail=0.066, free_tail=False, snout=0.009, ear=(0.0085, 0.0135, 25.0), nose_leaf=False,
                   fur="#7E5636", fur_tip="#B4875A", skin="#4A352C", membrane="#3A2A24", eye_r=0.0016,
                   mantle=None),
    "freetail": dict(scale=1.05, d3tip=(0.165, -0.034), d4tip=(0.128, 0.006), d5tip=(0.088, 0.03), fore=1.12,
                     tail=0.088, free_tail=True, snout=0.007, ear=(0.011, 0.012, 55.0), nose_leaf=False,
                     fur="#4E4038", fur_tip="#76655A", skin="#3A2E2A", membrane="#2F2622", eye_r=0.0017,
                     mantle=None, wrinkled=True),
    "nectar": dict(scale=1.1, d3tip=(0.145, -0.042), d4tip=(0.124, 0.016), d5tip=(0.1, 0.042), fore=1.04,
                   tail=0.03, free_tail=False, snout=0.02, ear=(0.006, 0.009, 15.0), nose_leaf=True,
                   fur="#8C6440", fur_tip="#C9A06E", skin="#5A3E30", membrane="#4A332A", eye_r=0.0022,
                   mantle=None),
    "flyingfox": dict(scale=3.4, d3tip=(0.15, -0.046), d4tip=(0.128, 0.02), d5tip=(0.104, 0.046), fore=1.0,
                      tail=0.0, free_tail=False, snout=0.016, ear=(0.006, 0.011, 10.0), nose_leaf=False,
                      fur="#33251E", fur_tip="#5A4232", skin="#2E211B", membrane="#3B2A22", eye_r=0.0032,
                      mantle="#C98A3E"),
}


def mirror(p, sx):
    return (p[0] * sx, p[1], p[2])


def points(sp):
    S = SPECIES[sp]
    f = S["fore"]
    P = {
        "S": (0.011, -0.016, 0.004), "E": (0.033, -0.004, 0.002),
        "W": (0.033 + 0.033 * f, -0.004 - 0.022 * f, 0.0),
        "H": (0.008, 0.022, -0.004), "Kn": (0.017, 0.036, -0.003), "A": (0.014, 0.047, -0.004),
        "tail0": (0.0, 0.026, 0.0), "tail1": (0.0, 0.026 + S["tail"], -0.004),
        "neck": (0.0, -0.022, 0.004), "headt": (0.0, -0.045, 0.008),
    }
    W = P["W"]
    P["T"] = (W[0] + 0.001, W[1] - 0.008, W[2] + 0.002)
    t3 = S["d3tip"]
    t4 = S["d4tip"]
    t5 = S["d5tip"]
    P["tip3"] = (t3[0], t3[1], 0.0)
    P["K3"] = (W[0] + (t3[0] - W[0]) * 0.47, W[1] + (t3[1] - W[1]) * 0.47 - 0.012, 0.0)
    P["tip2"] = (W[0] + (t3[0] - W[0]) * 0.62, W[1] + (t3[1] - W[1]) * 0.62 - 0.02, 0.0)
    P["K2"] = (W[0] + (P["tip2"][0] - W[0]) * 0.75, W[1] + (P["tip2"][1] - W[1]) * 0.75 - 0.004, 0.0)
    P["tip4"] = (t4[0], t4[1], 0.0)
    P["K4"] = (W[0] + (t4[0] - W[0]) * 0.55, W[1] + (t4[1] - W[1]) * 0.55 - 0.004, 0.0)
    P["tip5"] = (t5[0], t5[1], 0.0)
    P["K5"] = (W[0] + (t5[0] - W[0]) * 0.58, W[1] + (t5[1] - W[1]) * 0.58 - 0.002, 0.0)
    return P


def bones(sp):
    P = points(sp)
    b = [("body", (0, 0.022, 0.0), (0, -0.02, 0.003), None),
         ("head", P["neck"], P["headt"], "body")]
    if SPECIES[sp]["tail"] > 0:
        b.append(("tail", P["tail0"], P["tail1"], "body"))
    for sx, s in ((1, "L"), (-1, "R")):
        m = lambda k: mirror(P[k], sx)   # noqa: E731
        b += [(f"hum.{s}", m("S"), m("E"), "body"), (f"fore.{s}", m("E"), m("W"), f"hum.{s}"),
              (f"d1.{s}", m("W"), m("T"), f"fore.{s}"),
              (f"d2a.{s}", m("W"), m("K2"), f"fore.{s}"), (f"d2b.{s}", m("K2"), m("tip2"), f"d2a.{s}"),
              (f"d3a.{s}", m("W"), m("K3"), f"fore.{s}"), (f"d3b.{s}", m("K3"), m("tip3"), f"d3a.{s}"),
              (f"d4a.{s}", m("W"), m("K4"), f"fore.{s}"), (f"d4b.{s}", m("K4"), m("tip4"), f"d4a.{s}"),
              (f"d5a.{s}", m("W"), m("K5"), f"fore.{s}"), (f"d5b.{s}", m("K5"), m("tip5"), f"d5a.{s}"),
              (f"thigh.{s}", m("H"), m("Kn"), "body"), (f"shin.{s}", m("Kn"), m("A"), f"thigh.{s}")]
    return b
