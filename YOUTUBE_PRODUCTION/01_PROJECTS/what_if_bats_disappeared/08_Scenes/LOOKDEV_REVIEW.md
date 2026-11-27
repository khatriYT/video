# Look-dev Review: Episode 4 (Bats)

You asked me to inspect every scene before rendering and fix unfinished models, poor textures, inconsistent colours, lighting problems and weak backgrounds. This file is that inspection log: every issue I found, how I found it, and the fix.

- **Images:** `lookdev_review/` (JPEG copies).
- **Full-resolution look-dev renders:** written to `lookdev/`, which is not committed.

## 1. What changed from Episode 3 (pipeline)

| Area | Episode 3 (v2) | Episode 4 (v3) |
|---|---|---|
| Character modelling | Primitives and metaballs on an empty-joint puppet | **Signed-distance-field sculpting** (exact smooth unions and subtractions), meshed with Surface Nets and relaxed with Taubin smoothing, about 1 M quads per character (`tools/bats3d/sdf.py`) |
| Rigging | Rigid parts parented to empties | A real **armature with skinned meshes**. Weights are computed offline. Shirt weights are geometry-aware: sleeve surfaces follow the arm, torso surfaces the spine |
| Faces | A sphere head with painted features | Sculpted brow, nose with alae and nostrils, lips with a smile crease and dimples, cheeks, chin, ears with concha and tragus. Glossy eyeballs with procedural iris, limbal ring and pupil. Eyelid shells (blinks), lashes, brows |
| Hands | Mitten-like | Five fingers with three segments each, knuckles, finger pads, a thumb with thenar pad, and nails (tint channel) |
| Skin | Flat colour | **Subsurface scattering** (red-weighted radius), mottling, cheek/nose/ear blush, crease shadows, lip tint, freckles, pore and wrinkle bump, a light clear-coat |
| Cloth | Flat colours | Twill weave, fibre fuzz, sheen, colour variation, sculpted wrinkles, pockets with flaps and buttons, placket, collar, cuffs, polka-dot bandana, stitched bucket hat with brass eyelets, laced boots with tread soles |
| Bats | n/a | Rigged flyer: fur (particle strands), membrane wings stretched over 5 finger bones with a vein shader and back-lit translucency, thumb claws. Hanging roosters for caves. White-nose variant with fungal fuzz |
| Environments | Flat ground with scattered props | Art-directed sets with a sky that the camera sees separately from the ambient light that lights the scene. Volumetric haze, instanced leaf-card foliage, Geometry-Nodes scattering of grass and wildflowers, SDF-sculpted cliff and cave |
| Grade | AgX plus a vignette | AgX in the render, then a per-location grade: split toning, contrast curve, saturation, bloom, vignette, grain |

## 2. Inspection log (issue → fix)

### Pip v3 (`lookdev_review/00_*`, `01_*`)

| # | Found in review | Fix |
|---|---|---|
| P1 | First build: the eyes were missing from the face. A matrix was read before Blender had updated it, so the eyeballs landed at the feet as one huge sphere | `Rig.attach` now builds the transform from location, rotation and scale |
| P2 | The hat was too big and too low (covering the eyes); it looked like a pith helmet | Hat re-profiled with a lower crown, smaller brim, band and stitch rings; tilted 7° back; colour deepened |
| P3 | Hair locks stuck out like sausages, some on the face | Hair rebuilt as an SDF "hair mass" (an offset shell of the skull with curly lobes), limited to the sides and back and kept off the face and ears |
| P4 | Lips were swollen ("duck lips") | Lip volumes reduced twice. The smile crease now curves up at the corners, with corner dimples |
| P5 | The scarf was a striped "life-ring" torus and the collar a white cylinder | Bandana re-modelled as a rolled neckerchief with a knot and two tails, with a polka-dot fabric. The collar has folded points lying on the chest |
| P6 | Boxy, armour-like vest shoulders | Torso rebuilt with trapezius slopes and rounder shoulders. Armholes enlarged; V-opening widened |
| P7 | Thin, long legs | Looser cargo trousers with thigh pockets. Head scaled 1.13× for stylised appeal |
| P8 | Soles looked like flat plates under the boots | Soles now follow the boot footprint, with tread grooves |
| P9 | Splayed, claw-like fingers | Rest curl increased and finger spread reduced |
| P10 | Waving pose: the shirt side stretched up like a sheet (`04_skinning_bug_wave.jpg`) | **Geometry-aware shirt skinning**: sleeve surfaces follow the arm and torso surfaces the spine, blended at the armpit |
| P11 | Character frames rendered fully transparent (no mask) | The character-mask AOV is now added to every material in the character pass |

### Bats (`02_bat_myotis_and_white_nose.jpg`)

| # | Found | Fix |
|---|---|---|
| B1 | Fur strands were about a metre long. The particle "roughness" values are absolute distances | Roughness scaled to the hair length. Fur is now about 4 mm |
| B2 | The snout read as a pig nose | Tapered snout, smaller nose pad, slit nostrils, lips reshaped |
| B3 | Wing membranes were too orange | Translucency colour darkened; mix reduced to 0.3 |
| B4 | The hanging bat was an unreadable sausage | Re-designed: compact body, visible face, ears hanging down with tragus, folded wings as a leathery cape with forearm ridges and thumb claws, feet gripping |
| B5 | Cave plate: giant black glossy blobs. The hanging bat's eyes had been scaled to 1 m | Eye scale fixed (radius 1.6 mm). Affected plates (cave, fig tree) were re-rendered |

### Environments (`03_environments_first_pass.jpg`, `05_plates_review_pass1.jpg`)

| # | Found | Fix |
|---|---|---|
| E1 | Hill country: muddy magenta ground, sparse grass, cave hidden behind the rim | Camera-ray sky and scene ambient separated. Raking side sun. The cliff re-sculpted as a vertical limestone wall with stepped strata and the cave arch at its foot. Dense grass and wildflowers near the camera |
| E2 | Trees looked like smooth "broccoli" blobs | **Instanced leaf-card foliage**: thousands of leaves per near tree (broad oak leaves, juniper sprigs, long tropical leaves). Blob versions only on distant hills |
| E3 | Cliff looked like white popcorn | Warmer sandstone-limestone shader with strata and lichen, at a larger noise scale |
| E4 | Hibernaculum walls missing (an SDF sign error), then a black plate (camera inside the rock) | Plane sign fixed. Cave cameras moved inside the chamber. Cool bounce lights and a brighter teal ambient added |
| E5 | Stalactites looked like striped carrots | Irregular, wobbly, displaced stalactites with a wet translucent shader |
| E6 | Farm and agave: dark backlit foregrounds, sparse crops, thin white agaves | Side light plus sky-fill ambient. Corn rows 16/m². Agave redesigned (36–44 rigid V-section leaves, golden-angle phyllotaxis, waxy blue-green) and planted densely with Poisson spacing |
| E7 | Agave close-up: the flower cluster was a crude polygon blob | New detailed umbel: 46 tubular flowers, each with 6 stamens and anthers, on the hero stalk; the camera moved back to a 45 mm lens |
| E8 | Durian close-up nearly black | Warm hand-torch key from the camera side |
| E9 | Mine and night-sky plates flat | Ambient fill and a side key on the mine. Moonlit fields and town light clusters on the sky plate |
| E10 | A light-cache (bounce light) bake ran for over 15 minutes for one set on this CPU | Not used. Fill is designed with ambient-split skies and hidden bounce lights instead |

### Shot review during rendering (each finished shot composited and checked)

| # | Found | Fix |
|---|---|---|
| R1 | Durian close-up: the camera was inside the giant fig trunk (the hero fig and the durian branch shared a spot) | The durian scene moves the hero fig 9 m / 11 m away. The plate was re-rendered |
| R2 | Torches (head-lamp / hand torch) pointed at the ground; their direction was read before the rig had updated | View layer updated before aiming. Lamps are mounted on the rig at the origin, then the rig is placed |
| R3 | Agave close-up: the nectar bat was hidden behind the flower stalk | The bat is placed screen-left of the umbel, facing it, so face, tongue and wings read |
| R4 | Emergence swarm: individual bats were unreadable blobs far away. The column looked like scattered noise | Bats are emitted as a continuous ribbon that rises out of the cave mouth. Far bats are drawn as soft motion-blurred dashes, and near flybys use the 3D flight cycles. The dusk haze colour now matches the sky |
| R5 | Fact call-outs clipped long text (e.g. "1,300+ species") | Call-outs auto-fit: text is measured and scaled to the panel width |
| R6 | Corn-net shot: a corn leaf crossed the camera lens | Camera moved and the plant removed from the near-camera band |
| R7 | The first over-the-shoulder shot of Pip watching the bats (EMERGE_PIP) put Pip too small and off the column | Re-framed: low over-the-shoulder camera with a 24 mm lens, Pip at screen-left, the column rising in the right two-thirds. Plate and character pass re-rendered |
| R8 | Character shadows darkened a rectangle around the character (the shadow ratio was applied outside the rendered region) | Shadow and AO ratios apply only where the character pass actually rendered |
| R9 | Farm moths read as pairs of glowing white dots ("eyes") | Moths redrawn: depth-layered (a few large near ones, many small far ones), wing pair as a "V" around a dark body with a readable flap cycle, a faint motion trail, softened edges and depth-faded colour |
| R10 | Hanging-bat close-ups move very little but cost full render time | One frame rendered, then animated in compositing with a subtle breathing scale and drift. The camera move continues over it |
| R11 | **Corn and cotton fields were broken**: bare stalks, floating tassels, leaf clumps without stalks, and corn ears or cotton bolls lying on the soil like pebbles. Geometry Nodes "Separate Children" instances every object of a collection on its own, so each plant was scattered part by part | Multi-part plants now live in their own child collection and are instanced whole. A crop-free corridor follows each low camera's sight line, and spots around placed actors and props are cleared. Corn leaves are a deeper green. All 13 farm plates were re-rendered |
| R12 | Chapter 6 and "silhouette" backgrounds: a flat white disc on a gradient sky | A textured moon with maria, moonlit cloud wisps, a ridge line with gnarled bare trees in silhouette, and three bats scripted to fly across the moon disc |
| R13 | Agave close-up: the hovering nectar bat was nearly black (mean pixel value ~11/255) and half out of frame on the left | Compositing-side luminance lift (hue kept, saturation tempered, slightly warmed) plus a thin cool moonlight rim along the silhouette. A new camera move frames the bat fully and drifts toward it |
| R14 | Cave exit in late winter: the opening was a blown-out emissive blob | Replaced, for this shot only, with a real winter exterior: snowfield lit by an overcast sky, bare branching trees with snow drifts, a pale sky backdrop, falling snow |
| R15 | **Hanging-bat close-ups showed no bat** (white-nose close-ups, the "heart" close-up, the waking bat). The ceiling had been re-sculpted after these cameras were set, so the macro camera ended up about 10 cm inside the rock. Ray tests confirmed it | The macro camera is now settled from the hero bat: it is lowered and pulled back until it sits in open air with a clear line of sight. Cluster bats are kept out of the lens's view cone in front of the hero. The hero turns its fungus-covered face to the lens in three-quarter view (direction checked with a turnaround render), and the framing is aimed at the head with 30% more room. Plates and passes re-rendered |
| R16 | **Pip's vest was open at the back.** A V-opening cut tested the wrong half-space (characters face −Y), so it removed the back panel. From behind, the vest looked like a vest front, which made the over-the-shoulder shots confusing | Cut removed; the vest is closed front and back (turnaround checked). Re-rendered: the two shots that show Pip from behind |
| R17 | Opening shot: Pip's "look up" pose tilted the head back 42°, showing only the underside of the hat and the back of the head | Per-shot tilt scale; the opening shot uses 40% of the tilt, and the eyes and brows carry the rest of the upward look |
| R18 | Corn-net shot: Pip's lantern was a featureless overexposed sphere stuck to the hand, and a pitch-black hand shadow covered half his torso (sharp shadow maps + a point light 10 cm from the body) | A modelled lantern: metal base and cap, glowing glass with a bright flame core, four guard wires, a wire handle. It hangs upright from the grip with a gentle pendulum sway (the pivot follows the hand each frame instead of rotating rigidly with it). The lantern light casts shadows only in the plate |
| R19 | Sky-hunt shot ("bats climb hundreds of metres to hunt moths"): no bats visible; the camera looked down at dark farmland, where back-lit bats vanish | Camera tilted up so the bats silhouette against the moonlit sky above distant farm-town lights. Swarm brought closer (20 m). Textured moon |
| R20 | Lesser long-nosed bat comeback: a very dark, empty night field for a hopeful beat | Re-staged at blue hour like the neighbouring agave scenes: a low camera looking up at flowering agave stalks against the twilight sky, with a dense swarm of lit nectar bats around the blossoms |
| R21 | Bats crossing the moon were specks at 45 m | The three hero bats fly 20 m from the lens, large enough to read as bat silhouettes on the moon disc |
| R22 | Sky hunt, second pass: the lower half was a black void below the horizon, and the bats were dark specks on a dark sky | The camera looks higher into the moonlit sky; the far land has a dim moonlit tone; hundreds of distant farm and town lights reach the horizon (camera far-clip extended to 40 km for this view); the swarm is closer and its bats carry a cool moonlit tone |
| R23 | Bat-house shot: the "bat house" was a flat brown panel on a huge barn wall, unreadable | Modelled a pole-mounted two-chamber bat house (dark paint, overhanging roof, batten trim, vent slot, grooved landing plate, mounting bracket). It stands in the open left of the barn and silhouettes against the sunset sky. The farmer turns to look up at it, and bats emerge from its open bottom |
| R24 | Winter cave exit was overexposed by the cave grade | A dedicated cool "winter" grade without the cave exposure push |
| R25 | Chapter title "THE EXPERIMENT NOBODY WANTED" was clipped by its panel | Chapter panels grow with the title; the font shrinks only past the frame width |

### Render budget decisions (CPU-only machine)

- A character frame took about 110 s at first. I reduced it to about 45–50 s (with 4 renders sharing 4 cores) by:
  - simplifying the meshes by 60% with collapse decimation (no visible difference at these shot sizes);
  - using sharp shadow maps in character passes only (plates keep soft shadows);
  - using 6 anti-aliasing samples for character passes;
  - rendering only a tight region around each character.
- Frame rates (24 fps output):
  - characters: 12 fps;
  - slow, subtle shots: 8 fps;
  - hovering bats: 16 fps.
- Large bat swarms use **3D-rendered flight cycles**: 24 viewing angles × 12 wing positions per species and lighting. The compositor projects each bat with the plate camera, depth-tests it against the plate and applies atmospheric haze.

## 3. Still open (honest limitations)

- Everything renders in Eevee on a CPU. There is no ray-traced global illumination and no GPU. Fill light is designed by hand instead.
- Pip does not lip-sync. The narrator is off-screen (documentary style).
- Hanging bats show only breathing and shivering; their wings don't unfold.
- Camera moves are eased 2D moves over 3D plates. Characters and bats move in true 3D.
