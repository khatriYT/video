#!/usr/bin/env python3
"""Rebuild the local reference material for a competitor video and channel.

The repository is public, so competitor frames, thumbnails and contact sheets
are NOT committed (they are the competitor's copyrighted images). This script
re-creates them locally in about a minute, so a new session can re-inspect them.

What it fetches (all public, read-only):
  * video metadata + chapters        (yt-dlp, mweb client, Node as JS runtime)
  * YouTube storyboard sprites (sb0) (the scrub-preview images: 320x180, one
                                      frame every ~10 s; NOT the full video)
  * channel video list + per-video metadata + maxres thumbnails

What it writes (under <out_dir>):
  01_Competitor_Research/channel_videos.csv
  01_Competitor_Research/thumbnails/<id>.jpg              (gitignored)
  01_Competitor_Research/thumbnails_contact_sheet.jpg     (gitignored)
  02_Reference_Analysis/keyframes/KF###_tMMmSSs.jpg       (gitignored)
  02_Reference_Analysis/contact_sheets/CS##_*.jpg         (gitignored)
  02_Reference_Analysis/keyframe_metrics.csv              (measured colour/edge stats)
  02_Reference_Analysis/video_info.json                   (trimmed metadata)

Usage:
  python3 tools/fetch_reference_frames.py <video_url> <channel_url> <out_dir> [--skip-channel]

Requires: pip install "yt-dlp[default]" pillow numpy ; Node on PATH.
Full-resolution video download is NOT attempted: YouTube refuses it from cloud
IPs. Provide the video file yourself for motion analysis.
"""
import csv
import glob
import json
import os
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image, ImageDraw, ImageFont

YTDLP = ["yt-dlp", "--no-warnings", "--js-runtimes", "node",
         "--extractor-args", "youtube:player_client=mweb"]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def ytdlp_json(url, extra=()):
    out = subprocess.run(YTDLP + list(extra) + ["-J", url],
                         capture_output=True, text=True, timeout=300)
    if out.returncode != 0 or not out.stdout.strip():
        raise RuntimeError(f"yt-dlp failed for {url}: {out.stderr[-400:]}")
    return json.loads(out.stdout)


def fetch(url, path):
    with urllib.request.urlopen(url, timeout=60) as r, open(path, "wb") as f:
        f.write(r.read())


def font(size):
    try:
        return ImageFont.truetype(FONT, size)
    except OSError:
        return ImageFont.load_default()


def chapter_at(chapters, t):
    for c in chapters:
        if c["start_time"] <= t < c["end_time"]:
            return c["title"]
    return chapters[-1]["title"] if chapters else ""


def frame_metrics(img):
    """Measured stats used to separate painted plates from flat graphics."""
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    gray = luma
    edges = (np.abs(np.diff(gray, axis=0))[:, :-1] + np.abs(np.diff(gray, axis=1))[:-1, :]) > 0.08
    q = (a * 15).astype(np.uint8)
    n_colours = len(np.unique(q.reshape(-1, 3), axis=0))
    return {
        "mean_luma": round(float(luma.mean()), 3),
        "luma_p95": round(float(np.percentile(luma, 95)), 3),
        "mean_saturation": round(float(sat.mean()), 3),
        "warm_minus_cool": round(float((r - b).mean()), 3),
        "edge_density": round(float(edges.mean()), 3),
        "quantised_colours": int(n_colours),
    }


def build_keyframes(info, out):
    kf_dir = os.path.join(out, "02_Reference_Analysis", "keyframes")
    cs_dir = os.path.join(out, "02_Reference_Analysis", "contact_sheets")
    os.makedirs(kf_dir, exist_ok=True)
    os.makedirs(cs_dir, exist_ok=True)
    sb = next(f for f in info["formats"] if f["format_id"] == "sb0")
    rows, cols, w, h = sb["rows"], sb["columns"], sb["width"], sb["height"]
    duration = info["duration"]
    interval = 1.0 / sb["fps"]
    per_sheet = rows * cols
    frags = sb["fragments"]
    tmp = os.path.join(out, "02_Reference_Analysis", "_sprites")
    os.makedirs(tmp, exist_ok=True)

    def get(i_url):
        i, u = i_url
        p = os.path.join(tmp, f"{i:03d}.jpg")
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            fetch(u, p)
        return p

    with ThreadPoolExecutor(4) as ex:
        sprite_paths = list(ex.map(get, [(i, f["url"]) for i, f in enumerate(frags)]))

    chapters = info.get("chapters") or []
    metrics = []
    for s, p in enumerate(sprite_paths):
        im = Image.open(p).convert("RGB")
        for k in range(per_sheet):
            idx = s * per_sheet + k
            t = idx * interval
            if t > duration:
                continue
            r, c = divmod(k, cols)
            tile = im.crop((c * w, r * h, c * w + w, r * h + h))
            if max(e[1] for e in tile.getextrema()) < 8:  # padding tile
                continue
            name = f"KF{idx:03d}_t{int(t // 60):02d}m{int(t % 60):02d}s.jpg"
            tile.save(os.path.join(kf_dir, name), quality=92)
            m = {"keyframe": name, "time_s": round(t, 1),
                 "timecode": f"{int(t // 60):02d}:{int(t % 60):02d}",
                 "chapter": chapter_at(chapters, t)}
            m.update(frame_metrics(tile))
            metrics.append(m)
    for p in sprite_paths:
        os.remove(p)
    os.rmdir(tmp)

    with open(os.path.join(out, "02_Reference_Analysis", "keyframe_metrics.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(metrics[0].keys()))
        wr.writeheader()
        wr.writerows(metrics)

    # contact sheets: 30 frames each, labelled with timecode + chapter
    files = sorted(glob.glob(os.path.join(kf_dir, "*.jpg")))
    fnt, per, ncol, lab = font(15), 30, 6, 22
    for s in range(0, len(files), per):
        grp = files[s:s + per]
        nrow = (len(grp) + ncol - 1) // ncol
        sheet = Image.new("RGB", (ncol * (w + 6) + 6, nrow * (h + lab + 6) + 6), (25, 25, 25))
        dr = ImageDraw.Draw(sheet)
        for i, fp in enumerate(grp):
            idx = int(os.path.basename(fp)[2:5])
            t = idx * interval
            x, y = 6 + (i % ncol) * (w + 6), 6 + (i // ncol) * (h + lab + 6)
            sheet.paste(Image.open(fp), (x, y + lab))
            dr.text((x + 2, y + 2), f"{int(t // 60):02d}:{int(t % 60):02d}  {chapter_at(chapters, t)[:30]}",
                    fill=(255, 230, 120), font=fnt)
        t0 = int(os.path.basename(grp[0])[2:5]) * interval
        t1 = int(os.path.basename(grp[-1])[2:5]) * interval
        sheet.save(os.path.join(cs_dir, f"CS{s // per + 1:02d}_{int(t0 // 60):02d}m-{int(t1 // 60):02d}m.jpg"),
                   quality=88)
    return len(metrics)


def build_channel(channel_url, out):
    cr = os.path.join(out, "01_Competitor_Research")
    th = os.path.join(cr, "thumbnails")
    os.makedirs(th, exist_ok=True)
    flat = ytdlp_json(channel_url.rstrip("/") + "/videos", ["--flat-playlist"])
    ids = [e["id"] for e in flat["entries"]]
    flat_titles = {e["id"]: e.get("title") for e in flat["entries"]}

    def one(vid):
        try:
            d = ytdlp_json(f"https://www.youtube.com/watch?v={vid}",
                           ["--skip-download", "--ignore-no-formats-error"])
        except Exception as e:  # keep going; record the gap
            d = {"id": vid, "_error": str(e)[:200]}
        try:
            fetch(f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg", os.path.join(th, f"{vid}.jpg"))
        except Exception:
            pass
        return d

    with ThreadPoolExecutor(4) as ex:
        metas = list(ex.map(one, ids))

    rows = []
    for d in metas:
        vid = d["id"]
        rows.append({
            "video_id": vid,
            "upload_date": d.get("upload_date", ""),
            "title_watch_page": d.get("title", ""),
            "title_channel_list": flat_titles.get(vid, ""),
            "views": d.get("view_count", ""),
            "likes": d.get("like_count", ""),
            "comments": d.get("comment_count", ""),
            "duration_s": d.get("duration", ""),
            "chapters": len(d.get("chapters") or []),
            "url": f"https://youtu.be/{vid}",
            "error": d.get("_error", ""),
        })
    rows.sort(key=lambda r: r["upload_date"] or "")
    with open(os.path.join(cr, "channel_videos.csv"), "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)

    # thumbnail sheet in upload order
    fnt = font(20)
    tw, tht, ncol = 480, 270, 4
    have = [r for r in rows if os.path.exists(os.path.join(th, r["video_id"] + ".jpg"))]
    nrow = (len(have) + ncol - 1) // ncol
    sheet = Image.new("RGB", (ncol * (tw + 8) + 8, nrow * (tht + 34) + 8), (34, 34, 34))
    dr = ImageDraw.Draw(sheet)
    for i, r in enumerate(have):
        x, y = 8 + (i % ncol) * (tw + 8), 8 + (i // ncol) * (tht + 34)
        sheet.paste(Image.open(os.path.join(th, r["video_id"] + ".jpg")).convert("RGB").resize((tw, tht)), (x, y))
        dr.text((x, y + tht + 4), f"{r['upload_date']}  {r['views']:,} views" if r["views"] != "" else r["video_id"],
                fill=(240, 240, 240), font=fnt)
    sheet.save(os.path.join(cr, "thumbnails_contact_sheet.jpg"), quality=88)
    return len(rows), flat


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    video_url, channel_url, out = sys.argv[1:4]
    skip_channel = "--skip-channel" in sys.argv
    info = ytdlp_json(video_url)
    keep = {k: info.get(k) for k in ("id", "title", "channel", "channel_id", "uploader_id", "upload_date",
                                     "duration", "view_count", "like_count", "comment_count", "channel_follower_count",
                                     "categories", "tags", "chapters", "description", "width", "height", "fps")}
    keep["_fetched_note"] = "Counts are a snapshot at fetch time; storyboard frames are YouTube scrub previews."
    os.makedirs(os.path.join(out, "02_Reference_Analysis"), exist_ok=True)
    with open(os.path.join(out, "02_Reference_Analysis", "video_info.json"), "w") as f:
        json.dump(keep, f, indent=1, ensure_ascii=False)
    n = build_keyframes(info, out)
    print(f"keyframes: {n}")
    if not skip_channel:
        n_videos, _ = build_channel(channel_url, out)
        print(f"channel videos: {n_videos}")


if __name__ == "__main__":
    main()
