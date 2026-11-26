# Production Tracker: What If Every Vulture Disappeared? (Episode 3)

- **Created:** 2026-11-26.
- **Status:** review video exported. **Waiting for your approval** (final-video gate). The script gate is also still open.

| Phase | Status | Outputs | Approval needed | Next action |
|---|---|---|---|---|
| Topic approval | **Complete** | Vultures, chosen by you on 2026-11-26 ("I will go with your pick") | — | — |
| Scientific research | **Complete** | `03_Research/research_report.md`, `source_library.md` (20 sources), `claim_checklist.csv` (24 claims), `ecological_relationships.md` | — | — |
| Script draft | **Complete** | `04_Script/script_draft.md`, `script_final.md`, `script_sources.md` (1,355 words) | **Yes: still open.** Produced end-to-end at your request ("generate 10 minutes of video as soon as possible") | Review; revisions welcome |
| Storyboard | **Complete** | `06_Storyboard/storyboard.md`, `scene_list.csv`, `storyboard.json`, `asset_requirements.md` (74 scenes) | — | — |
| Style bible + 3D assets | **Complete** | `05_Style_Bible/STYLE_BIBLE_EP3.md`; procedural assets in `tools/vulture3d/lib.py` | — | — |
| Scene builds + renders | **Complete** | `08_Scenes/renders/` (26 stills, 3 animations, settings JSON per shot), `08_Scenes/render_log*.txt` | — | — |
| Animation / compositing | **Complete** | `09_Animation/SC001–SC074.mp4`, `scene_timing.json` | — | — |
| Narration | **Complete** | `10_Audio/narration/` (Kokoro `am_michael`, 74 files) | — | — |
| Music + SFX | **Complete** | `10_Audio/music/score_vultures.wav` (original, synthesized), `10_Audio/sound_effects/` | — | — |
| Edit + review export | **Complete** | `12_Exports/*_REVIEW.mp4`, `.srt`, chapters, `QC_REPORT.md`, `QC_contact_sheet.jpg`; edit package in `11_Edit/` | — | — |
| Final video approval | **Waiting for Approval** | — | **Yes** | Watch the review export and give notes |
| Thumbnail + packaging | Draft only | `14_Delivery/YOUTUBE_UPLOAD_DRAFT.md` (3 titles, 3 thumbnail concepts, description with sources) | **Yes** (title + thumbnail) | After video approval: render thumbnails from 3D assets |
| Delivery | Not Started | — | — | — |

## Known limitations

- **Animation:** most shots are 3D stills with eased camera moves. Three are true 3D animations (circling flock, orbit around the roost, final wide). Creature limbs are not rigged or walk-cycled; this was a CPU-only render budget decision.
- **Narration voice:** Kokoro TTS. Pronunciation of "Rüppell's" and "Sudarshan" was respelled for the TTS. Listen for any odd words.
- **Simplified visuals:**
  - The dog-vs-vulture trend chart is labelled "illustrative, not data".
  - The district map is labelled "schematic".
