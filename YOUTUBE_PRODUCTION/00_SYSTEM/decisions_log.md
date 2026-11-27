# Decisions Log

Newest entries first.

## 2026-11-26: Hardy Humans reference session

| ID | Decision | Reason | Decided by |
|---|---|---|---|
| D-011 | **Proposed** a hybrid 3D direction (Blender stills and depth layers, plus about 10 true-3D hero shots per episode) | The master prompt asks for 3D. A CPU-only benchmark makes full 3D animation of 12 min take about 120 h. The reference itself is 2D, so 3D would differentiate us | Claude, **pending user approval** |
| D-010 | New episode projects use the master prompt's `00_Project_Admin … 14_Delivery` layout (`tools/new_project.py`). Episodes 1–2 keep their old 01–10 layout | Follow the new master prompt without rewriting finished projects | Claude |
| D-009 | Reference material lives in `03_REFERENCE_LIBRARY/<channel>/`, not inside an episode | It is reusable across episodes | Claude |
| D-008 | **Competitor frames, thumbnails and contact sheets are not committed.** They are gitignored, and `tools/fetch_reference_frames.py` regenerates them in about 1 min | The GitHub repo is **public**; committing them would republish the competitor's copyrighted images | Claude |
| D-007 | Stopped trying to download the full reference video. Analysed YouTube's storyboard previews instead (225 frames, one every 9.92 s) | YouTube returned 403. Cycling download clients was blocked by the session's safety check, so it was not pursued | Claude (safety check) |
| D-006 | Moved this session to the user's "video" cloud environment, and added 3 `googlevideo.com` hosts | The default environment blocked YouTube. The hosts were added at the user's approval but did not enable the download | User approved |
| D-005 | Installed yt-dlp, OpenCV, PySceneDetect, Blender 4.0.2 and Mesa EGL **in the disposable cloud container only** | Needed for analysis and the 3D benchmark. Nothing was installed on the user's computer | Claude |

## Earlier (from the episode 1–2 sessions)

| ID | Decision |
|---|---|
| D-004 | Episode 2 topic: bees, chosen by Claude on the user's request |
| D-003 | Episode 1 topic: mosquitoes |
| D-002 | House style: 2D SVG, the mascot Pip (bucket hat, round glasses, olive vest) |
| D-001 | First competitor reference: Nobody Gets In (`00_SYSTEM/COMPETITOR_RESEARCH_REPORT.md`) |
