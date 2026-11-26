# House Style Bible v2: DRAFT (hybrid 3D)

- **Status:** draft, pending your approval of the visual direction.
- **Replaces:** nothing yet. Part B of `COMPETITOR_VISUAL_STYLE_GUIDE.md` (the 2D SVG house style used for episodes 1–2) stays valid until you approve this.
- **Inputs:**
  - Hardy Humans reference analysis (`03_REFERENCE_LIBRARY/HardyHumans/02_Reference_Analysis/`)
  - Blender benchmark (`CAPABILITY_REPORT.md`)
  - Your master prompt's 3D requirement

## 0. Direction in one paragraph

- A **stylized 3D world built in Blender** with a warm, matte "diorama" look.
- Recurring environments are real reusable 3D scenes, rendered from **fixed camera presets** and **named lighting presets**, so an "observation plate" can be shown at Hour 1 → Year 10 with perfect continuity. This is the one thing the competitor's AI plates cannot do.
- Our mascot **Pip** and the episode's creature are simple, toy-like 3D models built from primitives, so they stay identical in every shot.
- Facts are shown on flat **evidence cards** in our own palette.
- Motion is mostly eased camera moves over rendered stills or depth layers, plus a few true-3D hero animations per episode (render budget in the capability report).

## 1. Look and render settings

| Setting | Value |
|---|---|
| Engine | Eevee for finals (software OpenGL, about 25–60 s per 1080p frame); Workbench for layout previews |
| Resolution / frame rate | 1920×1080, 24 fps delivery. True-3D animation rendered at 12 fps ("on twos") and held, which halves the cost and suits the toy look |
| Materials | Matte, roughness 0.5–0.9, no mirror reflections. Soft subsurface (0.1–0.2) on Pip's head and creature bodies for warmth |
| Shading | Eevee soft shadows on, ambient occlusion on (distance 1 m), bloom subtle |
| Colour management | Filmic or AgX, look "Medium High Contrast" |
| Depth of field | Wide shots: off or f/8. Close-ups: f/1.8–2.8 on the subject. Can be applied in post on the background layer instead |
| Grain | Light film grain added in FFmpeg at assembly |

## 2. Character Bible

### CHR_PIP: Pip, field naturalist (our mascot)

Translated from the 2D spec. Proportions are in Blender units, where 1 BU = 1 m at "toy" scale.

| Part | Spec | Never changes |
|---|---|---|
| Head | UV sphere, r = 0.55. Off-white #F6F0E2, roughness 0.55, subsurface 0.15 | ✔ |
| Eyes | Two black spheres, r = 0.05, at ±0.17 x and 0.08 above the head centre, slightly inset | ✔ |
| Glasses | **Round wire glasses**: torus rings (r = 0.13, minor 0.012), dark brown #3B2A1E, plus a bridge | ✔ main identifier |
| Hat | **Mustard bucket hat** #F2B33D: a flattened cylinder crown plus a flared brim, with a band #C98A1E | ✔ |
| Mouth | Textured or shape-key curve: smile / "o" / flat / frown | Range only |
| Body | Capsule, height 1.0, r = 0.30 | ✔ |
| Vest | **Olive field vest** #6E8B3D, a shell over the capsule, with a chest-pocket bevel | ✔ |
| Arms / legs | Thin capsules, dark brown #2B2420. Round mitten hands in head colour. Brown boots #5A3B22 | ✔ |
| Prop | Satchel #8A5A35 (optional per scene) | — |
| Scale | Total height 2.2 BU (head about 1/3 of height, as in 2D) | ✔ |
| Personality | Curious, calm, slightly awkward. Leans in to look; head tilts; blinks every 3–5 s | — |
| Rig | Simple bone chain: root, spine, neck, head, arms (upper/lower), legs. Shape keys for mouth and blink | — |

**Deliverable after approval:**
- `05_Style_Bible/characters/CHR_PIP.blend`
- turnaround renders (front, ¾, side, back)
- an expression sheet

### CRE_<SPECIES>: episode creature (template)

Each episode defines:
- ID, name, species and real size, plus our toy-scale size relative to Pip;
- silhouette rules: the 2–3 features that make it recognisable at thumbnail size;
- palette (3–4 hex values), and material rules: feathers, fur or chitin simplified to matte shapes;
- eyes. Creatures get bigger, more expressive eyes than Pip; a convention carried over from the 2D mosquito;
- a motion library: idle loop, signature action (soaring, crawling, flying), exit;
- "Never change" details.

**Accuracy rule:** stylized but **anatomically honest**: correct leg count, wing type and diagnostic markings.

## 3. Environment Bible (template)

Each environment is one `.blend` file in `07_3D_Assets/` with:

| Field | Example |
|---|---|
| ID | `ENV01_OBSERVATION_PLATE` |
| Layout / scale | 40 × 40 BU ground; landmarks at fixed coordinates (e.g. acacia tree at (-6, 9), rock at (3, 4)) |
| Camera presets | `CAM_WIDE` (24 mm, eye level, horizon on the upper third), `CAM_MED`, `CAM_CU_<subject>`, `CAM_AERIAL`. Never moved between episodes' time-steps |
| Lighting presets | `LGT_DAWN`, `LGT_DAY`, `LGT_GOLDEN`, `LGT_OVERCAST`, `LGT_NIGHT`: sun angle and colour, world colour, practical lights |
| State switches | Collections or geometry-node inputs: `vegetation_density`, `decay_level`, `animal_count`, `water_level`, `season` |
| Palette | Earthy base from v1 B.5: ground #D9C49A, foliage #8FB27A / #6E9A5E, sky #BFD9D6, with one saturated accent per shot |
| Atmosphere | Mist volume or a fog plane for depth; light haze on distant layers |
| Continuity rules | Landmarks never move. The time-step changes only the state switches and the lighting |

## 4. Object Bible (template)

| Field | Spec |
|---|---|
| ID | `OBJ_<NAME>`, e.g. `OBJ_SPECIMEN_JAR`, `OBJ_FIELD_NOTEBOOK` |
| Model | Primitives and bevels, matte materials |
| Scale | Stated relative to Pip (Pip = 2.2 BU) |
| Reuse | Flagged reusable across episodes or episode-only |

## 5. Graphics, text and on-screen system (ours, not the competitor's)

| Element | Spec |
|---|---|
| Evidence card background | Deep forest slate **#14211C** (not their near-black navy), with cream #FFF6E0 text |
| Accents | Mustard #F2B33D (highlights), alarm red #E0533A (warnings and key numbers), leaf green #8FB27A (positive) |
| **Evidence tag** (new) | A small pill on fact cards: `STRONG EVIDENCE` (green), `DEBATED` (mustard), `SPECULATIVE` (grey). This is our science-channel differentiator |
| Time stamp (our version of a HUD) | Bottom-left field-notebook tab: `T+3 WEEKS · Gujarat, India` in a handwritten-style font, mustard tab |
| Chapter card | A field-notebook page flip showing the time-step ("WEEK 2") and the consequence ("THE DOGS"). Not their DAY / red-number layout |
| Captions | 2–4-word phrases, cream with a dark outline, lower third, as an optional burned-in track. A full SRT is always delivered |
| Font | A heavy rounded sans-serif for titles; a clean sans-serif for labels; one handwritten accent font for notebook elements |

## 6. Consistency rules

1. Every recurring asset has a stable ID and one master `.blend`. Scenes **link** (not append) characters and environments, so a fix propagates everywhere.
2. Never redesign Pip or the creature between shots. Any change needs a version bump (`CHR_PIP_v2`) and an entry in the decisions log.
3. Observation plates are rendered **only** from saved camera presets.
4. Lighting comes only from named presets. A new preset needs a name and a log entry.
5. Every render is saved with its scene ID: `SC###_preview.png`, `SC###_final.png`, plus `SC###_settings.json` (camera, lighting preset, state switches, engine, samples).
6. QC every shot for:
   - Pip's identifiers (hat, glasses, vest);
   - creature anatomy;
   - the landmarks in place;
   - no stray text;
   - the narration claim matching the image.
