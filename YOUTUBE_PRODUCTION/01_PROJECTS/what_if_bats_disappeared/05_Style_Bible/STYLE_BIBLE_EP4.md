# Episode 4 Style Bible: Bats (v3 "studio quality" pass)

- **Source of truth:** code.
  - SDF sculpts: `tools/bats3d/sdf.py`
  - Skeletons: `skeleton.py`, `batskel.py`
  - Characters: `human.py`, `bat.py`
  - Plants and materials: `flora.py`, `core.py`
  - Sets: `envs4.py`
  - Shots: `shots4.py`
  - Render: `render4.py`
  - Composite and grade: `compose4.py`
- **Model files:** generated into `07_3D_Assets/models/` (regenerate with `python3 tools/bats3d/sdf.py <models> pip,farmer,bat_myotis,bat_freetail,bat_nectar,bat_flyingfox,env`).
- **Inspection log:** `08_Scenes/LOOKDEV_REVIEW.md`.

## Design change (documented)

CHR_PIP was a round off-white sphere head in Episodes 1–3. You asked for refined facial anatomy (eyes, nose, mouth, ears, hands, fingers), so Pip is now a **stylised human naturalist**. The identity markers are unchanged:
- round dark wire glasses;
- mustard bucket hat with a darker band;
- olive field vest;
- warm, curious personality.

## Character Bible

| ID | Description | Never changes |
|---|---|---|
| CHR_PIP (v3) | Stylised human, 1.70 m, head scale 1.13 | See the CHR_PIP breakdown below |
| CHR_FARMER | Medium-deep skin (#9A6646); dark short hair and mustache. Red/navy plaid shirt; denim overalls (#3A5A8A); cream cap; brown boots | Cap + plaid + overalls |
| CRE_BAT_MYOTIS | Little brown bat: glossy brown fur (#7E5636 → tips #B4875A); dark skin (#4A352C); membranes #3A2A24 with a vein network and red translucency when back-lit; pointed ears with tragus; small black glossy eyes | White-nose variant adds white fungal fuzz on the muzzle, ears and forearms |
| CRE_BAT_FREETAIL | Brazilian / Mexican free-tailed bat: dark grey-brown; long narrow wings; broad forward ears; wrinkled lips; free tail | Narrow wings + free tail |
| CRE_BAT_NECTAR | Lesser long-nosed bat: long snout with a small nose leaf; golden-brown fur; large eyes | Long snout |
| CRE_BAT_FLYINGFOX | Fruit bat (scale 3.4×): dark body, golden mantle (#C98A3E), large eyes, fox-like muzzle | Golden mantle |

**CHR_PIP (v3) in detail**

| Feature | Design |
|---|---|
| Skin | #E0A986 with subsurface scattering, freckles, and rosy cheeks, nose and ears |
| Hair | Curly auburn (#7A3B1E) |
| Eyes | Hazel-green |
| Glasses | Round wire (#3B2A1E) |
| Hat | Mustard bucket hat (#E9A21A) with a dark band, stitching rings and brass eyelets |
| Clothes | Cream linen shirt with rolled sleeves; olive vest (#6E8B3D) with 4 flap pockets; red polka-dot bandana; slate cargo trousers (#3D4A5E); leather belt with brass buckle; laced leather boots |
| Bag | Canvas satchel |
| Caves | Adds a headlamp |

**Never changes:** glasses, bucket hat, olive vest, bandana, palette.

## Environment Bible

Every location has its own palette and light, held constant across all of its shots.

| ID | Palette | Key light | Shots |
|---|---|---|---|
| ENV_HILL (sinkhole cave, Texas) | Magenta → orange sunset sky; golden grass; bluebonnet blue, paintbrush red and daisy yellow wildflowers; sandstone-cream cliff; dark-green junipers and oaks | Low raking sun from the right (#FFA868); lavender sky fill | EMERGE_* |
| ENV_CAVE (hibernaculum) | Teal wet limestone; amber flowstone; warm headlamp (#FFE2B8); cold white daylight at the entrance | Headlamp / torch spot; teal bounce | HIB_* |
| ENV_FARM | Red barn (#B0302A) with white trim; white farmhouse with warm windows; green-gold corn; purple dusk or blue day | Dusk: low side sun (#FF9A62). Day: high warm sun. Night: blue moonlight | FARM_*, CORN_*, COTTON_* |
| ENV_AGAVE | Blue-green agave (#4E8C8E) on red-brown volcanic soil (#9A4A2E); golden flower stalks; violet hills | Sunset side light; blue hour; moonlight | AGAVE_* |
| ENV_TROPIC | Lush greens, orange figs, morning mist; durian at night with warm lanterns | Dawn back-light (#FFD58A) or moonlight plus a warm torch | TROPIC_FIG, DURIAN_NIGHT, CLEARING_* |
| ENV_SKY | Deep blue night, stars, moon, farm and town lights far below | Moon | SKY_HUNT, MOON_* |
| ENV_STUDIO | Teal → violet gradient | Key / fill / two coloured rims | STUDIO_* |
| ENV_MINE | Green hills, red rock, timber-framed entrance, banana plants; dusk | Side sun | MINE_RETURN |
| ENV_WIND | Sunset ridge with white turbines | Back-lit sun | WIND_RIDGE |

## Object Bible

| Object | Description |
|---|---|
| Agave rosette | Golden-angle phyllotaxis |
| Flowering stalk (quiote) | Detailed hero umbels |
| Corn plant | Stalk, 11 leaves, tassel and ear |
| Cotton plant | Leaves and bolls |
| Prickly pear | Pads, flowers and fruit |
| Bluebonnet / paintbrush / daisy | Wildflowers |
| Juniper / oak / fig / palm / banana / fern | Trees and understorey plants |
| Farm buildings and machinery | Barn, farmhouse, windmill, silo, fence, bat house, wind turbines; red tractor with sprayer (generic, no branding) |
| Exclosure net cage | Used in the corn experiment shot |
| Durian | Branch with flowers and spiky fruit |
| Hanging bat clusters | Cave set dressing |

## Render look

| Stage | Settings |
|---|---|
| Plates | 2304×1296, Eevee, 20 samples, soft shadows, contact shadows, GTAO, screen-space reflections, volumetric haze |
| Characters | Same camera; 6 samples; AOV mask; shadow and AO ratios against a character-free baseline; depth-tested against the plate depth |
| Grade (per location) | Exposure, saturation, contrast curve, split toning (cool shadows / warm highlights), bloom, vignette, fine grain |
| Output | 1920×1080, 24 fps |

## Continuity rules

1. **Locations:** each location uses one builder, so landmarks never move between shots. Only the camera, light state and actors change.
2. **Characters:** come from one cached SDF model set (`07_3D_Assets/models/`), so every shot uses the identical character.
3. **Sensitive content:**
   - No dead bats are shown.
   - Infant mortality appears only as data cards, with no imagery of babies or grief.
   - Disease is framed with evidence tags.
