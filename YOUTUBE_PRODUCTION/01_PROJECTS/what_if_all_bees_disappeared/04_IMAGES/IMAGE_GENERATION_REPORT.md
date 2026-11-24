# Image Generation Report: Episode 2 (Bees), 105 scenes

## Method
Original code-drawn illustrations in the house style, rendered by headless Chromium at 1920×1080. No AI image API was used.

| Module | Covers |
|---|---|
| `tools/draw3.py` | New, more detailed library for this episode |
| `tools/scenes_bees.py` | Scenes 001–035 |
| `tools/scenes_bees2.py` | Scenes 036–070 |
| `tools/scenes_bees3.py` | Scenes 071–105 |

Each still is a keyframe of the scene that also drives the animation. The image prompts in `../03_STORYBOARD/STORYBOARD.md` can be pasted into an AI image tool if you add one later.

## What's new vs. episode 1 ("more designed backgrounds, more detailed objects")
**Layered environments.** All are built from layers: sky gradients, sun rays, drifting clouds, distant tree lines, mid-ground hills, foreground flower beds and grass tufts.
- cottage garden in sunrise / day / sunset versions: tiled roof, smoking chimney, shutters, window boxes, picket fence, stepping-stone path, bird bath, hive
- supermarket produce aisle in one-point perspective, with stocked bins, price tags and ceiling lights
- kitchen with tiles, cabinets and window
- apiary in summer and snow versions, with barn and hedges
- honeycomb hive interior: procedural hex cells, capped and open
- patchwork farmland with river, barn and orchard
- almond orchard rows in perspective, blooming and bare
- Sichuan terraced mountains
- greenhouse
- city with rooftop gardens
- farmyard
- highway
- lab
- alpine meadow
- soil cross-section
- prehistoric landscape

**Creatures.** Honeybee (with pollen baskets, queen-with-crown and courier-cap variants), fuzzy bumblebee (with a buzz-shake mode), solitary, mason and leafcutter bees, wasp, butterfly, hummingbird, bee-eater, songbird, field mouse, cow, Varroa mite, cocoa midge, robot bee.

**Food and props.**
- produce: apple, cherry, blueberry, strawberry, almond, avocado, melon, pumpkin, coffee, bread, rice, corn, potato, honey jar, cocoa pod and chocolate
- beekeeping and farm gear: hive boxes with a lifting lid, smoker, beekeeper with veil, ladders, feather brush, hive trucks, tractor sprayer, bulldozer
- garden items: bee hotel, window box
- charts and objects: hourglass, balance scale, dominoes, price tags, pie charts
- maps: world, California, USA

## QC (all 105 stills reviewed in contact sheets)
Fixes made:

| Scene | Problem | Fix |
|---|---|---|
| — | Cottage roof tiles spilled outside the roof | Clipped to the roof |
| 26 | "Human view / bee view" label split badly | Labels drawn in-scene |
| 37 | Stamp ran off the right edge | Stamp positioning now edge-aware |
| 39 | Food labels overlapped | Smaller text |
| 57 | Farmer's hat covered his face | Hat moved up |
| 68 | Magnolia unclear | Replaced with a large blossom |
| 71, 90 | Text shown twice | Kinetic text removed where the scene already draws it |
| pop titles | Word spacing too tight | Per-character width estimate |
