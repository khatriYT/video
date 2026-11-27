# Episode 3 Style Bible: Vultures (hybrid 3D)

- **House style:** `00_SYSTEM/STYLE_BIBLE_v2_DRAFT.md`.
- **Source of truth:** every asset is procedural Python in `tools/vulture3d/lib.py`, and every shot is defined in `tools/vulture3d/shots.py`. Re-running a shot rebuilds identical geometry, materials, cameras and lights.
- **Render settings:** each render's settings are saved next to it as `08_Scenes/renders/<SHOT>_settings.json`.

## Render look

| Setting | Value |
|---|---|
| Engine | Blender 4.0 Eevee (software OpenGL) |
| Stills | 2304×1296, 16 samples |
| Animations | 1600×900, 8 samples, 12 fps, held on twos |
| Colour | AgX, "Punchy" look; soft shadows; ambient occlusion; subtle bloom |
| Atmosphere | Mist-pass haze on geometry only; the sky comes from the environment pass |
| Post (in the compositor) | Eased camera move over the still (zoom ≤ 1.1), vignette, light grain |

## Character Bible

| ID | What | Never changes |
|---|---|---|
| CHR_PIP | Mascot field naturalist. Off-white sphere head (#F6F0E2); round dark-brown wire glasses; mustard bucket hat (#F2B33D) with a darker band; olive vest (#6E8B3D); dark limbs; brown boots. Poses: stand / binoculars / point / look_up / wave | Hat, glasses, vest, colours, 2.2 BU height |
| CHR_VILLAGER | Same body language as Pip, with varied skin tones (#8D5A3B, #B27A50, #C68B5E), hair and clothing colours. Background only, 0.75 scale | Neutral, respectful depiction |
| CRE_VULTURE | Gyps-type vulture with an Indian-vulture palette: buff body (#A8875F), dark flight feathers (#3A2D24), cream ruff (#EAE1CF), bare grey-brown head and neck (#6E6763), dark hooked beak (#57504A), short grey legs. Poses: stand, perch, feed, spread, soar (fingered primaries), fallen (lying flat, eyes closed). About 1.1 BU standing; about 3.1 BU wingspan | Bald head plus white ruff plus buff body plus dark primaries; correct leg count |
| CRE_DOG | Indian pariah dog: tan (#C79B62), darker ears, curled tail. Poses: stand, sniff, walk, sit | Tan coat, curled tail |
| CRE_CROW | House crow: black body, grey nape (#5D5A5C) | Grey nape |

## Object Bible

| ID | What | Notes |
|---|---|---|
| OBJ_COW | Zebu: grey (#B9B2A6), hump, darker muzzle and head, dark horns. States: standing, carcass, bloated | **Non-graphic by design:** no blood or wounds, eyes closed |
| OBJ_BONES | Stylized dry remains (ribs, skull, long bones), bone-white | No flesh |
| OBJ_VIAL | Generic injectable vial with a red band and cap | No brand or label text |
| OBJ_TREE_DEAD / _NEEM / _ACACIA | Roost tree; neem canopy; flat-topped acacia | Fixed seeds and positions |
| OBJ_HOUSE | Village houses: flat parapet or tile roof | Fixed layout in ENV_DUMP |
| OBJ_TOWER | Tower of Silence, stylized circular stone wall on a hill. Optional solar mirrors | **No remains depicted** |
| OBJ_AIRLINER | Simple white airliner for the altitude-record shot | — |

## Environment Bible

| ID | Layout | Cameras | Lighting presets | State switches |
|---|---|---|---|---|
| ENV_DUMP (observation plate) | Carcass at (0, 0); dead roost tree at (−7.5, 7); neem trees at (10, 14), (−16, 20), (22, 30), (−30, 38); 7 houses at y ≈ 33–38; hills at y ≈ 160 | CAM_WIDE (−1.5, −15.5, 3.4) → (1, 4, 1.2), 30 mm. CAM_LOW (4.6, −5.2, 1.1), 42 mm. CAM_CU_DOG. CAM_PIP. CAM_WIDE_HIGH | dawn, morning, noon_hot, overcast, golden, dusk, night | hour0, arrive, feed, day1, day3, week2, year1, year10, nepal |
| ENV_ROOST | Dead tree at the origin (scale 1.6), two neems, hills | Portrait, head close-up, group wide, orbit (A02) | golden, dawn, overcast, day | number of birds |
| ENV_SKY | Sky dome with procedural clouds, ground far below | Low-angle look-up | morning, day | — |
| ENV_ROOM | Table, plaster walls, window light | Vial close-up | day | — |
| ENV_VILLAGE | Street with 8 houses, neem, rocks | Street, yard | dusk, morning | dogs, cow |
| ENV_TOWER | Hill, tower, neem ring, far skyline | Wide | dawn, monsoon | mirrors |
| ENV_SAVANNA | Acacia hero tree plus 4 far acacias, hills | Wide | golden, dusk | birds on/off |

## Continuity rules applied

1. **ENV_DUMP time steps** (P00, P03, P04, P05, P06, P07) use the **same CAM_WIDE**. Landmarks never move; only state and light change.
2. **Vulture design** is identical in every shot: same function, same materials.
3. **Sensitive content:**
   - Carcasses are grey and stylized, with eyes closed and no blood.
   - The Tower of Silence shows no human remains.
   - The fallen vulture is shown lying still with closed eyes.

---

## v2 (2026-11-26): fully animated characters and detailed backgrounds

This version was made in response to your feedback: "it's just images, not animation… good 3D characters… well detailed backgrounds".

### Characters (`tools/vulture3d/rigs.py`)

Every character is now a **jointed puppet**: an empty hierarchy with detailed parts. Parts are merged per joint for render speed.

| ID | v2 build | Motions |
|---|---|---|
| CRE_VULTURE | Feather-scallop body shader; 30-tuft fluffy ruff; two-segment bare neck; brow ridges; glossy eyes with highlights; cere and hooked bill; folded wings (coverts plus 6 flight feathers); spread wings (9 secondaries and coverts on the arm, 7 fingered primaries on the hand); 6-feather tail fan; scaly legs with 4 toes and talons | idle, feed (dip/tug cycle), display (spread wings), circle/soar (banking), glide, flap, land (descend, flap, settle), hop, fallen |
| CRE_DOG | Fur shader, cream chest and muzzle, ears with inner colour, glossy nose, eyes with highlights, two-segment curled tail, legs with knees and paws; 4 coat colours | walk, trot, sniff-walk (path following), sniff, tug, sit, idle, bark; tail wag, ear flicks, blinks |
| CHR_PIP | Same identity as before (off-white head, round glasses, mustard bucket hat with band, olive vest). Added: eyes with highlights, brows, blush, smile/talk mouths, shirt and sleeves, pockets and buttons, satchel, trousers, boots, binoculars | idle, walk, wave, point, binoculars, look up, talk, shrug, worried; blinks; lip flaps while talking |
| CHR_VILLAGER | Pip's rig with hair and coloured clothes; varied skin tones | walk, idle, talk |
| CRE_CROW | House crow with a grey nape; wing joints | hop, peck, fly |
| OBJ/CRE_COW | Standing zebu: hump, dewlap, horns, ears, tail tuft | chew/head bob, tail swish, ear flicks, blinks |

### Environments (`tools/vulture3d/envs2.py`)

- **Ground:** a multi-layer terrain shader (dirt, soil, dry grass, green patches, pebbles, bump) with a worn path.
- **Plants:** 4 grass varieties, wildflowers (4 colours) and flowering shrubs.
- **Trees:** branching neem, acacia and dead trees; distant tree lines.
- **Village houses:** wall bands, framed doors and windows with shutters, steps, rooftop water tanks, clotheslines, clay pots, charpais, haystacks; lit windows at dusk and night.

### Render method (`tools/vulture3d/render3.py`, `compose3.py`)

| Step | What it does |
|---|---|
| 1. Plates | Each detailed background is rendered once: 2304×1296, Eevee, 16 samples |
| 2. Character pass | Every frame at 12 fps, from the same camera, terrain and lights. The characters are cut out with a per-object mask (an AOV), and their shadows come from Eevee's shadow pass, normalised against a character-free baseline |
| 3. Compositing | The plate is darkened by the character shadows, the characters are composited on top, then the eased camera move, overlays and particles are applied |
| 4. Full-3D shots | Two shots (SC071 orbit, SC073 dolly) are rendered entirely in 3D with characters and moving cameras |
