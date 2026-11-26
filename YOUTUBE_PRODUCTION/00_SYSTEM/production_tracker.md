# Production Tracker: Channel Pipeline / Episode 3

- **Updated:** 2026-11-26.
- **At the start of every session:** read this file, then `decisions_log.md`, then `SYSTEM_CONFIG.json`.

## Current position

**Waiting for approval** of two things:

1. The Episode 3 topic.
2. The visual direction: hybrid 3D, 2D, or full 3D.

| # | Phase | Status | Outputs | Approval needed | Next action |
|---|---|---|---|---|---|
| 0 | Environment inspection | **Complete** | `00_SYSTEM/CAPABILITY_REPORT.md` | — | — |
| 1 | Competitor research: Hardy Humans | **Complete** (limits noted) | `03_REFERENCE_LIBRARY/HardyHumans/01_Competitor_Research/competitor_report.md`, `channel_videos.csv` | — | — |
| 2 | Reference video deep analysis (`wqMaepNXeBc`) | **Complete for stills; motion Blocked** | `03_REFERENCE_LIBRARY/HardyHumans/02_Reference_Analysis/` (`report.md`, `scene_timeline.csv`, `visual_style_bible.md`, `camera_and_lighting_notes.md`, `motion_notes.md`; frames local only) | Optional: upload the MP4 | If the file arrives: scene detection, then fill in `motion_notes.md` |
| 3 | Initial house style bible v2 (hybrid 3D) | **Waiting for Approval** | `00_SYSTEM/STYLE_BIBLE_v2_DRAFT.md` | **Yes**: visual direction | After approval: build `CHR_PIP.blend`, turnarounds, the first observation plate |
| 4 | Topic selection | **Waiting for Approval** | `00_SYSTEM/TOPIC_SHORTLIST_EP3.md` | **Yes** | After approval: `python3 tools/new_project.py <slug>`, then Phase 8 research |
| 5 | Scientific research | Not Started | `research/` files per master prompt §8 | — | — |
| 6 | Script draft | Not Started | `04_Script/script_draft.md` | **Yes** (script gate) | — |
| 7 | Storyboard | Not Started | `06_Storyboard/` | — | — |
| 8 | 3D assets, scenes, renders | Not Started | `07_3D_Assets/`, `08_Scenes/` | — | — |
| 9 | Animation | Not Started | `09_Animation/` | — | — |
| 10 | Narration, music, SFX, edit | Not Started | `10_Audio/`, `11_Edit/` | — | — |
| 11 | Review export | Not Started | `12_Exports/` | **Yes** (final video gate) | — |
| 12 | Thumbnail and packaging | Not Started | `13_Thumbnails/`, `14_Delivery/` | **Yes** (title + thumbnail) | — |

## Earlier episodes

| Episode | Result | Open item |
|---|---|---|
| Ep 1: Mosquitoes | Complete (12:06) | Script approval is still marked "Waiting for User" in that project's `PROJECT_STATUS.md` |
| Ep 2: Bees | Complete (12:02) | Same: script approval still marked "Waiting for User" |

## Known limitations

- **Reference video:** full download is impossible from this cloud server (YouTube 403). Only 225 storyboard stills were analysed.
- **Rendering:** CPU-only Blender. Eevee takes about 25 s per frame and full 3D animation does not fit. Plan for the hybrid approach.
- **No denoiser** in Ubuntu's Blender build.
- **Ephemeral container:** tools must be reinstalled each session unless a setup script is saved.
