# Decisions Log: What If All Bats Disappeared?

| Date | Decision | Reason | By |
|---|---|---|---|
| 2026-11-26 | Topic: bats ("What If All Bats Disappeared? A Fungus Already Ran the Experiment") | You asked me to "select next topic". Bats was the highest-scoring remaining shortlist topic (26/30), with colourful locations | Assistant, at your request |
| 2026-11-26 | Produce the video end-to-end; the script gate stays open for review | Your instruction for this episode was to upgrade the visuals and make the video | Assistant |
| 2026-11-26 | Pip redesigned from a sphere-head mascot to a stylised human (glasses, bucket hat, vest kept) | You asked for refined facial anatomy, hands and fingers | Assistant (documented in STYLE_BIBLE_EP4.md) |
| 2026-11-26 | New v3 pipeline: SDF-sculpted characters, skinned armatures, PBR materials, art-directed environments, graded compositing | You asked for studio-quality characters and colourful environments | Assistant |
| 2026-11-26 | No new software installed. Blender lacks numpy here, so the heavy geometry runs in system Python (numpy) and Blender loads the results | Your rule: no installs without asking | Assistant |
| 2026-11-26 | No light-cache (bounce light) bake | Over 15 minutes per set on this CPU; replaced with designed ambient/bounce lighting | Assistant |
| 2026-11-26 | Character passes at 12 fps (8 fps for slow shots, 16 fps for hovering bats); output at 24 fps | CPU-only render budget | Assistant |
| 2026-11-26 | Infant-mortality findings shown only as data cards | Sensitive subject | Assistant |
| 2026-11-26 | Not used: the "1,000 mosquitoes an hour" claim, Bracken Cave insect tonnage, and the "10,000 ft" altitude figure | Not well supported, or sources conflict | Assistant |
