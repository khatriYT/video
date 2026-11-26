# Capability Report

**Inspected:** 2026-11-26.

## Where this runs

Claude Code is running in a **managed cloud container**, not on your own computer:
- Ubuntu 24.04.5 LTS, x86_64.
- **4 vCPU, 15 GiB RAM, no GPU.**
- The disk allowance had about 60 GB free at start.

The container is **ephemeral**:
- Anything installed here (Blender, pip packages, TTS models) disappears when the session ends.
- Only what is committed and pushed to GitHub survives. Large media go through Git LFS.
- A setup script for the environment can reinstall the tools automatically; see the last section.

Nothing was installed, bought or changed on your own computer. No API keys were seen, used or stored.

## Status table

| Tool / capability | Status | Detail |
|---|---|---|
| Claude Code (cloud session) | **Ready** | Files, shell, git push to `ccr-82bff6bd-fiyrgo`, web search and page fetching, GitHub tools |
| Python 3.13.18 + numpy 2.5, Pillow 13.0, onnxruntime 1.29 | **Ready** | Pre-installed |
| OpenCV 5.1, PySceneDetect 0.7.3, yt-dlp 2026.11.23 (+ yt-dlp-ejs) | **Ready (installed this session)** | pip, inside the container only |
| FFmpeg 6.1.1 / ffprobe | **Ready** | Assembly, scene detection, encoding |
| ImageMagick (`convert`, `montage`) | **Ready** | Contact sheets, thumbnails |
| Node 22 | **Ready** | Also used as yt-dlp's JavaScript runtime |
| Chromium + Playwright | **Ready** | Renders our existing SVG animation pipeline (`tools/render.py`) |
| **Blender 4.0.2** | **Available, configured this session** | Installed from Ubuntu's repositories, plus Mesa EGL libraries for headless OpenGL. Benchmark below |
| Blender denoiser (OpenImageDenoise) | **Not available in this build** | Ubuntu's package is built without OIDN, so Cycles renders are noisy unless samples are high. The official blender.org build includes OIDN, but would need `download.blender.org` allowed on the network (your approval) |
| GPU / VRAM | **None** | CPU only. GPU rendering, local Stable Diffusion, ComfyUI and local video models are impractical here |
| ComfyUI / local image generation | **Not installed; not practical** | CPU-only diffusion takes minutes per image |
| Kokoro TTS (local, used for episodes 1–2) | **Needs configuration** | The pip package and model files (`kokoro-v1.0.onnx`, `voices-v1.0.bin`) must be re-downloaded each new container. The download host may need allowing |
| AI image/video/voice services (Midjourney, OpenAI Images, Runway, Kling, Luma, Pika, ElevenLabs, etc.) | **Requires a paid account / API key** | None configured. Not used without your explicit approval |
| CapCut | **Not available / not automatable here** | Desktop app, not on this Linux container. We deliver an edit package instead (numbered clips, audio stems, SRT, timeline CSV) |
| YouTube metadata, thumbnails, storyboard previews | **Ready** | After switching this session to your "video" environment |
| YouTube full-video download | **Blocked** | YouTube returns HTTP 403 for media streams to this cloud IP. Further workarounds were stopped by the session's safety check. **Manual step:** upload the MP4 if you want motion analysis |

## Network

- This session was moved to your existing **"video"** environment, which allows the YouTube hosts and the Git LFS hosts.
- Three YouTube media-server hosts (`*.googlevideo.com` edge nodes) were added at your approval. They did not make full downloads work (YouTube refuses with 403), so you may remove them in the environment settings if you wish.

## Blender render benchmark (this container)

The test scene is deliberately simple (`tools/blender_benchmark.py`): a stylized character, 5 trees, sun + area light, depth of field, rendered at 1920×1080.

| Engine | Time per frame | Notes |
|---|---|---|
| Workbench | 2.8 s | Grey viewport shading; previews only |
| **Eevee** (software OpenGL via Mesa) | **25 s** | Good stylized look: soft shadows, ambient occlusion |
| Cycles, 64 samples, no denoiser | 71 s | Visible noise; needs about 256+ samples or the official build's denoiser |

### What this means for a 10–12-minute video

At 24 fps, a 12-minute video is 17,280 frames:

| Approach | Estimated render time |
|---|---|
| Full 3D animation, Eevee, 1080p | About 120 h, even for this trivial scene. **Not practical** |
| Hybrid: every shot rendered as a 3D still (or 2–3 depth layers), animated with camera moves in FFmpeg, plus about 10 short true-3D hero animations at 12 fps | **About 8–14 h of background rendering.** Practical |

## Recommended setup script (optional)

These commands ran successfully in this session. Saving them on the "video" environment reinstalls the tools automatically in future sessions:

```bash
pip3 install -q "yt-dlp[default]" opencv-python-headless scenedetect
DEBIAN_FRONTEND=noninteractive apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq blender libegl1 libegl-mesa0 libgl1-mesa-dri
```
