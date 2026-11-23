# Image Generation Report: scenes 001–010

## Method
No AI image-generation API is configured in this environment. Images are **original, code-drawn vector illustrations**:

- `tools/draw.py` holds the house-style library (Pip, supporting cast, mosquito, props).
- `tools/scenes_mosquito.py` holds the per-scene compositions.
- Headless Chromium (Playwright) renders them at 1920×1080 PNG.

Each still is the keyframe of the same scene definition that drives the animation. Stills and clips therefore always match.

The storyboard's image prompts are written so they can be pasted directly into an AI image tool (Midjourney, DALL·E, Imagen, Flux, etc.) if you add one later.

## Reference assets (generated before scenes)
| File | Content | Also copied to |
|---|---|---|
| `characters/pip_character_sheet.png` | Pip in 5 poses plus the hat | `02_SHARED_ASSETS/characters/` |
| `characters/supporting_cast_and_mosquito.png` | Scientist A and B, parent, child, mosquito, mosquito "gone" pose | `02_SHARED_ASSETS/characters/` |
| `backgrounds/bg_bedroom_night.png` | Night bedroom plate | `02_SHARED_ASSETS/backgrounds/` |
| `backgrounds/bg_space_earth.png` | Space plus Earth | `02_SHARED_ASSETS/backgrounds/` |
| `backgrounds/bg_lab_wide.png` | Wide lab plate (3,200 px scene width) | `02_SHARED_ASSETS/backgrounds/` |
| `backgrounds/bg_dawn_pond.png` | Dawn hill, pond, reeds | `02_SHARED_ASSETS/backgrounds/` |
| `backgrounds/bg_sunrise_hills.png` | Sunrise hills | `02_SHARED_ASSETS/backgrounds/` |
| `objects/obj_specimen_jar.png` | Specimen jar with mosquito | `02_SHARED_ASSETS/reusable_objects/` |

## Scene images
| Scene | File | Matches narration | QC result |
|---|---|---|---|
| 001 | `scenes/scene_001.png` | Midnight, mosquito drops | Pass after fix: moved the "z" letters off the mosquito |
| 002 | `scenes/scene_002.png` | Trillions gone (globe plus swarm) | Pass |
| 003 | `scenes/scene_003.png` | Buzzing in your ear | Pass |
| 004 | `scenes/scene_004.png` | Itchy bites | **Regenerated.** v1 had Pip standing outside the bed and scratching with the wrong hand. v2 has Pip sitting up in bed, scratching the bitten arm. |
| 005 | `scenes/scene_005.png` | No more malaria (bed net lifted) | Pass |
| 006 | `scenes/scene_006.png` | "Sounds perfect, right?" | Pass |
| 007 | `scenes/scene_007.png` | Scientist A, "go ahead" | Pass |
| 008 | `scenes/scene_008.png` | Scientist B, "not so sure" | Pass |
| 009 | `scenes/scene_009.png` | "So let's find out" (hat drops on) | Pass |
| 010 | `scenes/scene_010.png` | Title question at dawn | Pass. Title text is intentional. |

QC checklist applied to each image (style guide B.9):

- Ink colour and line weight
- Pip's identifiers (mustard bucket hat, round glasses, olive vest)
- Palette
- 16:9 at 1920×1080
- No stray text
- No distorted limbs
- Subject matches the narration

All 18 PNGs were verified on disk at 1920×1080.

## Not yet generated
Scenes 011–068. Their prompts are complete in `../03_STORYBOARD/STORYBOARD.md`.
