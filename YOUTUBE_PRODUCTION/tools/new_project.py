#!/usr/bin/env python3
"""Create a new episode workspace using the master-prompt folder layout.

Usage: python3 tools/new_project.py <slug> "<Working Title>"
Creates YOUTUBE_PRODUCTION/01_PROJECTS/<slug>/ with 00_Project_Admin ... 14_Delivery,
an initial production_tracker.md, decisions_log.md, project_config.json and
asset_manifest.csv. Refuses to touch an existing folder.
"""
import csv
import datetime
import json
import os
import sys

DIRS = [
    "00_Project_Admin",
    "01_Competitor_Research",
    "02_Reference_Analysis/keyframes", "02_Reference_Analysis/contact_sheets", "02_Reference_Analysis/reports",
    "03_Research",
    "04_Script",
    "05_Style_Bible/characters", "05_Style_Bible/environments", "05_Style_Bible/objects",
    "06_Storyboard",
    "07_3D_Assets/models", "07_3D_Assets/materials", "07_3D_Assets/textures", "07_3D_Assets/rigs",
    "08_Scenes/blender", "08_Scenes/renders", "08_Scenes/previews",
    "09_Animation",
    "10_Audio/narration", "10_Audio/music", "10_Audio/sound_effects",
    "11_Edit",
    "12_Exports",
    "13_Thumbnails",
    "14_Delivery",
]
PHASES = ["Topic approval", "Scientific research", "Script draft", "Script approval", "Storyboard",
          "Style bible + 3D assets", "Scene builds + renders", "Animation", "Narration", "Music + SFX",
          "Edit + review export", "Final video approval", "Thumbnail + packaging", "Delivery"]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    slug, title = sys.argv[1], sys.argv[2]
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "01_PROJECTS", slug)
    if os.path.exists(root):
        sys.exit(f"refusing: {root} already exists")
    for d in DIRS:
        os.makedirs(os.path.join(root, d))
    today = datetime.date.today().isoformat()
    admin = os.path.join(root, "00_Project_Admin")
    with open(os.path.join(admin, "project_config.json"), "w") as f:
        json.dump({"slug": slug, "working_title": title, "created": today,
                   "system_config": "../../00_SYSTEM/SYSTEM_CONFIG.json",
                   "style_bible": "../../00_SYSTEM/STYLE_BIBLE_v2_DRAFT.md",
                   "reference_library": "../../03_REFERENCE_LIBRARY/",
                   "video": {"resolution": "1920x1080", "fps": 24},
                   "secrets": "never stored here; use environment variables / environment secrets"}, f, indent=2)
    with open(os.path.join(admin, "production_tracker.md"), "w") as f:
        f.write(f"# Production Tracker: {title}\n\nCreated {today}.\n\n"
                "| Phase | Status | Outputs | Approval needed | Next action |\n|---|---|---|---|---|\n")
        for p in PHASES:
            gate = "Yes" if "approval" in p.lower() or p.startswith("Thumbnail") else ""
            status = "Complete" if p == "Topic approval" else "Not Started"
            f.write(f"| {p} | {status} |  | {gate} |  |\n")
    with open(os.path.join(admin, "decisions_log.md"), "w") as f:
        f.write(f"# Decisions Log: {title}\n\n| Date | Decision | Reason | By |\n|---|---|---|---|\n"
                f"| {today} | Topic approved: {title} | | User |\n")
    with open(os.path.join(admin, "production_log.md"), "w") as f:
        f.write(f"# Production Log: {title}\n\n## {today}\n- Project created with tools/new_project.py\n")
    with open(os.path.join(admin, "asset_manifest.csv"), "w", newline="") as f:
        csv.writer(f).writerow(["asset_id", "type", "file", "version", "status", "used_in_scenes", "notes"])
    print(root)


if __name__ == "__main__":
    main()
