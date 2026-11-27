"""Episode 4 shot list (v3). Every 3D scene in the storyboard maps to one entry here.

Fields:
  env, state, env_kw        environment builder + time of day / variant
  cam                       (location, target, lens[, dof_fstop])
  actors                    animated 3D actors rendered in the character pass (see render4.ACTORS)
  props                     static set dressing added to the plate (bat clusters, net cage, lamp...)
  swarm                     2D-composited bat/moth swarm from pre-rendered 3D sprite cycles
  lamp                      a spot light (headlamp / torch) in plate and character pass
  full                      True -> rendered fully in 3D every frame (studio shots)
"""
try:
    from mathutils import Vector
except ImportError:      # outside Blender (compositor / audio): plain tuples are fine
    Vector = tuple
V = Vector


def S(env, state="", cam=None, actors=(), props=(), swarm=None, lamp=None, full=False, env_kw=None, fx=()):
    return dict(env=env, state=state, cam=cam, actors=list(actors), props=list(props), swarm=swarm, lamp=lamp,
                full=full, env_kw=env_kw or {}, fx=list(fx))


PIP_HILL = (-3.4, -10.6)
SHOTS = {
    # ---------------- hibernaculum
    "HIB_ENTER": S("cave", "healthy", ((-1.9, -3.9, 1.35), (0.5, 0.3, 2.8), 22),
                   actors=[("pip", "pip", 2.75, "look_up", dict(lamp=True))],
                   props=[("clusters", "healthy")], lamp="pip", fx=["dust"]),
    "HIB_FUNGUS_CU": S("cave", "infected", ((0.62, 0.18, 3.33), (0.8, 0.6, 3.36), 85, 8.0),
                       actors=[("hanger", "myotis", "hero", "breathe", dict(wns=1.0))],
                       props=[("clusters", "infected")], lamp="cam_left"),
    "HIB_EMPTY": S("cave", "empty", ((-1.9, -3.9, 1.35), (0.5, 0.3, 2.8), 22), props=[("clusters", "empty")],
                   lamp="cam", fx=["dust"]),
    "HIB_CHAPTER": S("cave", "healthy", ((-2.4, -3.0, 1.2), (1.0, 1.2, 3.0), 18), props=[("clusters", "healthy")],
                     lamp="cam", fx=["dust"]),
    "HIB_CLUSTER": S("cave", "healthy", ((-0.9, -1.4, 1.5), (0.8, 0.6, 3.5), 32), props=[("clusters", "healthy")],
                     lamp="cam", fx=["dust"]),
    "HIB_HEART": S("cave", "healthy", ((0.6, 0.2, 3.33), (0.8, 0.6, 3.36), 85, 8.0),
                   actors=[("hanger", "myotis", "hero", "breathe", dict(wns=0.0))],
                   props=[("clusters", "healthy")], lamp="cam_left"),
    "HIB_FUNGUS_CU2": S("cave", "infected", ((0.95, 0.25, 3.3), (0.8, 0.6, 3.36), 85, 8.0),
                        actors=[("hanger", "myotis", "hero", "breathe", dict(wns=1.0))],
                        props=[("clusters", "infected")], lamp="cam_left"),
    "HIB_WAKE": S("cave", "infected", ((0.62, 0.18, 3.33), (0.8, 0.6, 3.36), 85, 8.0),
                  actors=[("hanger", "myotis", "hero", "wake", dict(wns=1.0))],
                  props=[("clusters", "infected")], lamp="cam_left"),
    "HIB_SNOW_EXIT": S("cave", "empty", ((2.4, 3.6, 1.3), (3.6, 11.6, 1.8), 26), props=[("clusters", "empty")],
                       fx=["snow"]),
    "HIB_HOPE": S("cave", "hope", ((-3.0, -3.6, 1.2), (0.8, 0.6, 3.2), 24), props=[("clusters", "hope")],
                  lamp="cam_warm", fx=["dust"]),
    # ---------------- hill country cave (Bracken-like)
    "EMERGE_TITLE": S("hill", "sunset", ((4, -27, 1.5), (0, 6, 7.5), 22), swarm=("emerge", "freetail", "sunset", 0.45)),
    "EMERGE_PIP_WAVE": S("hill", "sunset", ((-2.0, -15.0, 1.45), (-3.4, -10.6, 1.35), 38),
                         actors=[("pip", "pip", 0.25, "wave", {})], swarm=("emerge", "freetail", "sunset", 0.25)),
    "EMERGE_SUNSET": S("hill", "sunset", ((-14, -30, 3.0), (2, 10, 5.5), 24), swarm=("emerge", "freetail", "sunset", 0.15)),
    "EMERGE_CHAPTER": S("hill", "sunset", ((11, -22, 2.0), (-2, 8, 4.5), 28), swarm=("emerge", "freetail", "sunset", 0.3)),
    "EMERGE_WIDE": S("hill", "sunset", ((2, -36, 1.2), (0, 8, 11), 20), swarm=("column", "freetail", "sunset", 1.0)),
    "EMERGE_PIP": S("hill", "dusk", ((-2.2, -14.8, 1.55), (-0.6, 8, 5.0), 24),
                    actors=[("pip", "pip", 3.05, "binoculars", {})], swarm=("column", "freetail", "dusk", 1.0)),
    "EMERGE_HUNGRY": S("hill", "dusk", ((-3, -5, 0.6), (0, 8, 6.0), 22), swarm=("column", "freetail", "dusk", 1.0)),
    "EMERGE_MOON_PIP": S("hill", "night", ((-0.2, -14.2, 0.9), (-4.6, -6.0, 3.6), 30),
                         actors=[("pip", "pip", 3.4, "look_up", dict(awe=True))], swarm=("moon", "freetail", "moon", 0.5)),
    "EMERGE_END": S("hill", "night", ((0, -32, 2.0), (0, 8, 8.5), 24), swarm=("moon", "freetail", "moon", 0.4)),
    # ---------------- farm
    "FARM_DUSK_WIDE": S("farm", "dusk", ((2, -36, 3.2), (2, 20, 5.0), 28), fx=["fireflies"]),
    "FARM_SONAR": S("farm", "dusk", ((-8, -6, 1.6), (5, 12, 4.5), 28), swarm=("hunt", "myotis", "dusk", 0.15),
                    fx=["moths", "sonar"]),
    "FARM_DAY_CHAPTER": S("farm", "day", ((-20, -30, 4.0), (6, 18, 4.0), 24)),
    "FARM_MOTHS": S("farm", "dusk", ((-1.0, -7.2, 1.5), (-1.5, -2.0, 1.45), 35),
                    actors=[("farmer", "farmer", 0.0, "worried", {})], fx=["moths_dense"]),
    "FARM_SPRAY": S("farm", "day", ((8, -27, 4.4), (-2, -15, 1.2), 28),
                    actors=[("tractor", (-2.0, -23.0), (-2.0, -9.0))], env_kw=dict(sprayer=False), fx=["spray"]),
    "FARM_DAY_CORN": S("farm", "day", ((6, -42, 1.8), (6, -20, 2.2), 30)),
    "FARM_DUSK_EMPTY": S("farm", "dusk", ((-10, -32, 3.4), (8, 20, 6.0), 26), fx=["moths"]),
    "FARM_SPRAY2": S("farm", "day", ((-11, -6, 4.0), (-2, -16, 1.2), 30),
                     actors=[("tractor", (-2.0, -22.0), (-2.0, -10.0))], fx=["spray"]),
    "FARM_HOUSE_NIGHT": S("farm", "night", ((-22, 12, 2.0), (-14, 30, 3.0), 35), fx=["moths_porch"]),
    "FARM_BATHOUSE": S("farm", "dusk", ((2.5, 6.0, 1.6), (8.3, 16.0, 4.0), 30), env_kw=dict(bathouse=True),
                       actors=[("farmer", (4.6, 10.6), 2.7, "look_up", {})], swarm=("bathouse", "myotis", "dusk", 0.2)),
    "COTTON_DUSK": S("farm", "dusk", ((0, -42, 2.0), (0, -10, 3.5), 28), env_kw=dict(crop="cotton"),
                     swarm=("hunt", "freetail", "dusk", 0.35)),
    "CORN_NET": S("farm", "night", ((-3.0, -37.0, 1.8), (-8.0, -30.0, 1.6), 30), props=[("net", (-8.0, -30.0))],
                  actors=[("pip", (-5.4, -32.4), 0.9, "lantern", {})], lamp="lantern", fx=["moths"]),
    "CORN_NIGHT_BATS": S("farm", "night", ((5, -46, 1.2), (5, -20, 4.0), 24), swarm=("hunt", "myotis", "moon", 0.5),
                         fx=["moths"]),
    # ---------------- agave
    "AGAVE_CHAPTER": S("agave", "sunset", ((8, -25, 2.0), (-4, 20, 4.0), 24)),
    "AGAVE_WIDE": S("agave", "sunset", ((-12, -22, 3.0), (4, 18, 4.0), 22)),
    "AGAVE_BAT_CU": S("agave", "blue", ("flower", 0.75, 45, 2.8), actors=[("nectar", "flower", "hover", {})],
                      fx=["pollen"]),
    "AGAVE_FARM": S("agave", "sunset", ((3.5, -17, 1.6), (0, -6, 1.2), 32), env_kw=dict(stalks=True),
                    actors=[("farmer", (1.2, -2.0), 3.14, "walk_to", dict(to=(1.2, -9.5)))]),
    "AGAVE_BLUE_HOUR": S("agave", "blue", ((0, -20, 1.5), (0, 25, 5.0), 24), swarm=("agave", "nectar", "dusk", 0.3)),
    "AGAVE_RECOVERY": S("agave", "night", ((6, -18, 1.2), (-2, 20, 6.0), 22), swarm=("agave", "nectar", "moon", 0.8)),
    "AGAVE_NIGHT_EMPTY": S("agave", "night", ((-6, -14, 1.2), (0, 15, 5.0), 26), fx=["moths"]),
    # ---------------- tropics
    "TROPIC_FIG": S("tropic", "dawn", ((-6, -20, 2.5), (0, 0, 8.0), 26), env_kw=dict(scene="fig"),
                    props=[("foxes_hanging", None)], swarm=("fig", "flyingfox", "dawn", 0.25)),
    "DURIAN_NIGHT": S("tropic", "night", ("durian", 1.4, 50, 3.2), env_kw=dict(scene="durian"), lamp="cam_warm",
                      actors=[("nectar", "durian", "hover", dict(sp="nectar"))], swarm=("durian", "nectar", "moon", 0.1)),
    "CLEARING_GROW": S("tropic", "dawn", ((0, -14, 1.6), (0, 6, 0.9), 28), env_kw=dict(scene="clearing"),
                       actors=[("seedlings", "grow")], swarm=("fly_over", "flyingfox", "dawn", 0.06), fx=["seeds"]),
    "CLEARING_BARE": S("tropic", "dawn", ((0, -14, 1.6), (0, 6, 0.9), 28), env_kw=dict(scene="clearing", bare=True)),
    # ---------------- sky / moon
    "SKY_HUNT": S("sky", "night", ((0, 0, 0), (0, 100, -14), 24), swarm=("sky", "freetail", "moon", 0.6), fx=["moths"]),
    "MOON_CHAPTER": S("sky", "night", ((0, 0, 0), (19, 100, 25), 45), swarm=("silhouette", "freetail", "moon", 0.25),
                      env_kw=dict(moon_scene=True)),
    "MOON_SILHOUETTE": S("sky", "night", ((0, 0, 0), (19.5, 100, 25.5), 90), swarm=("silhouette", "freetail", "moon",
                                                                                 0.12), env_kw=dict(moon_scene=True)),
    # ---------------- studio
    "STUDIO_WING": S("studio", "", ((0.0, -2.6, 1.55), (0, 0, 1.45), 50), actors=[("studio_bat", "flyingfox")],
                     full=True),
    "STUDIO_XRAY": S("studio", "", ((0.0, -2.3, 1.5), (0, 0, 1.45), 50), actors=[("studio_bat", "flyingfox")],
                     full=True, fx=["xray"]),
    # ---------------- mine / wind
    "MINE_RETURN": S("mine", "", ((6, -16, 2.0), (0, 1, 2.2), 28), swarm=("mine", "flyingfox", "dusk", 0.25)),
    "WIND_RIDGE": S("wind", "", ((0, -70, 3.0), (0, 40, 42), 24), actors=[("rotors", "slow")],
                    swarm=("hunt", "freetail", "sunset", 0.15)),
}

# character-pass frame rates (default 12): slow/subtle motion at 8, hovering wings at 16
for _k in ("HIB_FUNGUS_CU", "HIB_HEART", "HIB_FUNGUS_CU2", "FARM_BATHOUSE", "EMERGE_MOON_PIP", "HIB_ENTER",
           "EMERGE_PIP", "CORN_NET", "FARM_MOTHS"):
    SHOTS[_k]["fps"] = 8
for _k in ("AGAVE_BAT_CU", "DURIAN_NIGHT"):
    SHOTS[_k]["fps"] = 16

# hanging-bat close-ups barely move: render one frame, breathe it in compositing
for _k in ("HIB_FUNGUS_CU", "HIB_HEART", "HIB_FUNGUS_CU2"):
    SHOTS[_k]["hold"] = True
for _k in ("STUDIO_WING", "STUDIO_XRAY"):
    SHOTS[_k]["fps"] = 8
SHOTS["DURIAN_NIGHT"]["fps"] = 12

# compositing-side lighting help for an under-lit hero: exposure lift (1 - (1-c)^g) and a cool moonlight rim
SHOTS["AGAVE_BAT_CU"]["char_gain"] = 3.5
SHOTS["AGAVE_BAT_CU"]["char_rim"] = ((0.6, 0.72, 1.0), 0.4)
