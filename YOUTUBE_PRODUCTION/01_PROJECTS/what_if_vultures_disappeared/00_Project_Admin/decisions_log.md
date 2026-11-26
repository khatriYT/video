# Decisions Log: What If Every Vulture Disappeared?

| Date | Decision | Reason | By |
|---|---|---|---|
| 2026-11-26 | Topic approved: What If Every Vulture Disappeared? | | User |
| 2026-11-26 | Produce end-to-end without pausing at the script gate | User asked to "generate 10 minutes of video as soon as possible"; script left open for review | User |
| 2026-11-26 | Visual direction: hybrid 3D (Blender Eevee stills + camera moves, 3 true-3D animations, flat evidence cards) | Recommended option; CPU-only render budget | Claude (user went with "your pick") |
| 2026-11-26 | Claims corrected during research: no "pH 1" stomach claim; no unverified "tens of millions" population; fly-doubling study placed in Costa Rica (not Kenya); rabies toll given as "about a third of global deaths" (WHO) | Accuracy | Claude |
| 2026-11-26 | Feral-dog causality tagged DEBATED; mortality/cost numbers tagged ESTIMATE on screen | Separate evidence from estimates | Claude |
| 2026-11-26 | Sensitive imagery stylized: grey carcass with closed eyes, no blood; Tower of Silence shown without remains | Respect and ad-suitability | Claude |
| 2026-11-26 | **v2 rebuild:** every 3D scene animated (rigged puppet characters, 12 fps character passes); detailed backgrounds; layered plate + character-pass render method | User feedback: "it's just images not animation… all characters moving… good 3D characters… well detailed background" | User |
| 2026-11-26 | Character passes at 12 fps (held on twos), 1600×900 close / 1280×720 wide with render regions; plates at 2304×1296 / 16 samples | CPU-only Eevee: about 5–7 s per character frame; a full-scene per-frame render would have taken about 17 h | Claude |
