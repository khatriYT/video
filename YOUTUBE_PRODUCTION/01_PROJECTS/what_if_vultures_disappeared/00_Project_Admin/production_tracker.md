# Production Tracker: What If Every Vulture Disappeared? (Episode 3)

- **Created:** 2026-11-26.
- **Status:** **v2 animated review video exported** (2026-11-26). **Waiting for your approval** (final-video gate). The script gate is also still open.
- **v2 changes** (your feedback: "it's just images, not animation…"):
  - every 3D scene is animated with rigged characters;
  - detailed backgrounds;
  - same narration, music and 10:00 timing.

| Phase | Status | Outputs | Approval needed | Next action |
|---|---|---|---|---|
| Topic approval | **Complete** | Vultures, chosen by you on 2026-11-26 ("I will go with your pick") | — | — |
| Scientific research | **Complete** | `03_Research/research_report.md`, `source_library.md` (20 sources), `claim_checklist.csv` (24 claims), `ecological_relationships.md` | — | — |
| Script draft | **Complete** | `04_Script/script_draft.md`, `script_final.md`, `script_sources.md` (1,355 words) | **Yes: still open.** Produced end-to-end at your request ("generate 10 minutes of video as soon as possible") | Review; revisions welcome |
| Storyboard | **Complete** | `06_Storyboard/storyboard.md`, `scene_list.csv`, `storyboard.json`, `asset_requirements.md` (74 scenes) | — | — |
| Style bible + 3D assets | **Complete** | `05_Style_Bible/STYLE_BIBLE_EP3.md`; procedural assets in `tools/vulture3d/lib.py` | — | — |
| Scene builds + renders | **Complete (v2)** | `08_Scenes/renders3/plates/` (27 detailed plates; JPEG copies committed), character passes and full-3D orbit (frames not committed; rebuild with `tools/vulture3d/render3.py`). v1 stills remain in `08_Scenes/renders/` | — | — |
| Animation / compositing | **Complete (v2)** | 45 animated 3D scenes (`tools/vulture3d/compose3.py`) and 29 animated cards; `09_Animation/scene_timing.json` | — | — |
| Narration | **Complete** | `10_Audio/narration/` (Kokoro `am_michael`, 74 files) | — | — |
| Music + SFX | **Complete** | `10_Audio/music/score_vultures.wav` (original, synthesized), `10_Audio/sound_effects/` | — | — |
| Edit + review export | **Complete** | `12_Exports/*_REVIEW.mp4`, `.srt`, chapters, `QC_REPORT.md`, `QC_contact_sheet.jpg`; edit package in `11_Edit/` | — | — |
| Final video approval | **Waiting for Approval** | — | **Yes** | Watch the review export and give notes |
| Thumbnail + packaging | Draft only | `14_Delivery/YOUTUBE_UPLOAD_DRAFT.md` (3 titles, 3 thumbnail concepts, description with sources) | **Yes** (title + thumbnail) | After video approval: render thumbnails from 3D assets |
| Delivery | Not Started | — | — | — |

## Known limitations

- **Animation (v2):**
  - Characters are rendered at 12 fps and held on twos; camera moves are at 24 fps.
  - One shot (SC071) has a true 3D camera orbit. The others use eased 2D camera moves over detailed 3D plates.
  - The reason is the CPU-only render budget.
- **Narration voice:** Kokoro TTS. Pronunciation of "Rüppell's" and "Sudarshan" was respelled for the TTS. Listen for any odd words.
- **Simplified visuals:**
  - The dog-vs-vulture trend chart is labelled "illustrative, not data".
  - The district map is labelled "schematic".
