# Image Generation Report: all 98 scenes (v2)

## Method
No AI image API is configured, so every image is an **original code-drawn vector illustration** in the house style:

| Module | Covers |
|---|---|
| `tools/draw.py` | Characters, mosquito, core props |
| `tools/draw2.py` | Environments, creatures and infographics |
| `tools/scenes_mosquito.py` | Scenes 001–010 |
| `tools/scenes_mosquito2.py` | Scenes 011–048 |
| `tools/scenes_mosquito3.py` | Scenes 049–098 |

Each still (`scenes/scene_###.png`, 1920×1080) is a keyframe of the same scene definition that drives the animation, so stills and clips always match.

The image prompts in `STORYBOARD.md` remain usable with an AI image tool later.

## Library added for v2
- **Environments:**
  - meadow (day and dusk), dusk backyard, underwater cross-section
  - tundra, boreal forest, bog, night sky
  - chalkboard, lab, town, hospital ward, school, tropical valley, rainforest
  - museum wall, sepia history scenes
- **Creatures:**
  - aquatic: fish, larva, pupa, tadpole, dragonfly nymph
  - insects and spiders: dragonfly, spider and web, moth, beetle, bee, hoverfly
  - birds and mammals: swallow or shorebird, bat, caribou, wolf
  - others: shark, snake, dinosaur silhouette, vulture silhouette, blunt-leaf orchid
- **Infographics and props:**
  - charts and maps: podium and medal, bar chart, Africa heat map, icon grid, family-tree diagram, pie chart, Panama map, city map
  - objects: amber, fossil slab, egg raft, bucket, tyre, barrel, window screen, sprayer, cage, file cards, stamps, calendar

## QC
All 98 stills were reviewed in contact sheets against the narration and the style-guide checklist (B.9). Fixes made:

| Scene | Problem | Fix |
|---|---|---|
| 001 | Sleep "z"s overlapped the mosquito | Moved the "z"s |
| 004 | Pip stood outside the bed and scratched with the wrong hand | Redrawn |
| 016 | Pip cut off at the frame edge | Moved inward |
| 073 | Panama canal line too faint; workers covered the label | Stronger canal line, label moved |

Intentional on-screen text includes the title, chart labels, years, "MALARIA, DENGUE, ZIKA", "77%", "TESTING" and "ABANDONED".
