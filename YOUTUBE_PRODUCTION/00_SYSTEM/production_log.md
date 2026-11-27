# Production Log

Important actions and errors, newest first.

## 2026-11-26 (UTC)

**Reference video access**
- oEmbed for `wqMaepNXeBc` worked once the session was on the "video" environment: Hardy Humans, "What If You Were the Last Human on Earth for 3 Years? (Full Story)".
- yt-dlp `web`, `ios` and `android_vr` clients: "Sign in to confirm you're not a bot".
- The `mweb` client with Node as the JavaScript runtime returned metadata, 44 chapters, storyboards and one 360p format.
- Downloading that 360p format failed:
  - first, the proxy refused the `googlevideo.com` media hosts; 3 were added with the user's approval;
  - after that, YouTube itself returned **HTTP 403** on the media stream.
- A further attempt to test other clients was **denied by the session's safety check**. Stopped.

**Analysis**
- Fetched the 25 storyboard sheets for `sb0` (3×3 tiles of 320×180 each), giving 225 frames covering 0:00–37:12.
- Built 8 contact sheets.
- Annotated all 225 frames by eye (`tools/reference_labels_HH_wqMaepNXeBc.py` → `scene_timeline.csv`).
- Measured colour and edge stats (`keyframe_metrics.csv`).
- Channel: 23 videos' metadata and thumbnails. Title A/B testing observed on 2 videos.

**Blender**
- Installed Blender 4.0.2 (apt).
- The first renders aborted: `libEGL.so.1` missing. Fixed by installing `libegl1`, `libegl-mesa0` and `libgl1-mesa-dri` (surfaceless EGL fallback works).
- Cycles: `OPENIMAGEDENOISE` enum is not present, because Ubuntu's build has no OIDN. Benchmark ran with denoising off.
- Results at 1080p: Workbench 2.8 s, Eevee 25.0 s, Cycles (64 samples) 70.8 s.

**Repository**
- Repo visibility checked: **public**. Competitor images are gitignored; see D-008.
