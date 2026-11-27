# Reference Video Analysis: "What If You Were the Last Human on Earth for 3 Years? (Full Story)"

- **Video:** https://youtu.be/wqMaepNXeBc, by Hardy Humans (`@HardyHumans`)
- **Analysed:** 2026-11-26
- **Duration:** 37:12. Native upload resolution unknown; the highest stream offered to this server was 640×360 at 30 fps.
- **Upload date:** 2026-11-21. Snapshot on 2026-11-26: 320,804 views, 1,757 likes, 320 comments.
- **Data files in this folder:**
  - `scene_timeline.csv`: 225 sampled frames, each with frame type, shot, environment, caption word, description and measured colour stats
  - `keyframe_metrics.csv`: the measured stats on their own
  - `video_info.json`: metadata and the 44 chapters
  - `keyframes/` and `contact_sheets/`: local only, gitignored; rebuild them with `tools/fetch_reference_frames.py`

> ## Evidence level: read this first
> **What was inspected:** YouTube's own scrub-preview "storyboard" images. That is **225 frames at 320×180, one every 9.92 s, covering the full 37:12** [VERIFIED]. I looked at every one of them on the contact sheets.
>
> **What was not inspected:**
> - **The video itself.** YouTube returned HTTP 403 for the media stream from this cloud server. Trying more download workarounds was stopped by the session's safety check, so I did not pursue it.
> - **Therefore:**
>   - no motion, cut timing, transitions, audio, music or narration was observed;
>   - nothing between samples was seen;
>   - no scene-cut detection was possible.
>
> **How claims are tagged in this report:**
> - **[VERIFIED]:** seen in the samples or read from YouTube's public data.
> - **[MEASURED]:** computed from the sample pixels. These are approximate: 320×180 JPEGs.
> - **[INFERRED]:** my reading of the evidence. Check it against the real video.
>
> **To close the gap:** supply the video file (an MP4 at any resolution). The motion, editing and audio sections can then be filled in properly. See `motion_notes.md`.

---

## 1. Headline findings

1. **The reference is not 3D.** [VERIFIED]
   - Flat 2D vector characters are layered over richly detailed, painterly 2D background plates. Those plates have a soft "global illumination" look, which is why they can read as 3D at a glance.
   - Infographics are flat vector graphics.
   - Nothing in the samples shows real 3D camera parallax or 3D character rendering.
   - The backgrounds are very probably **AI-generated stills** [INFERRED]. Evidence:
     - storybook-realist detail density;
     - painterly texture;
     - small layout drifts between versions of the "same" location;
     - a different finish from the clean vector characters.
2. **The look is a three-layer system** [VERIFIED]:
   - (a) painted environment plates;
   - (b) flat round-headed characters composited on top;
   - (c) flat infographic cards.

   About 51% of samples are plates, 33% are graphics and maps, and 8% are character close-ups (counts in §3).
3. **Recurring, evolving locations carry the passage of time** [VERIFIED].
   - The same NYC street plate appears at least 8 times:
     - Day 1: bare trees, sunrise
     - Day 12: overcast
     - Day 21: dog pack
     - Day 50: golden hour
     - Day 70: lush green
     - Day 302: snow
     - Day 365: weeds and rust
     - Day 730: cracked, overgrown road
   - The rooftop plate appears at least 16 times: night, storm, smoke, signal fire, garden and dusk.
   - **This is the most transferable technique for an ecology channel**: one fixed viewpoint whose ecosystem visibly changes over time.
4. **Every chapter is a day-stamp plus one concrete problem plus one real fact** [VERIFIED from chapters and description].
   - There are 44 chapters in 37:12, averaging **51 s each**.
   - Examples: "Day 3 · The Water", "Day 12 · The Smell", "Day 21 · The Pack".
5. **Text on screen is constant** [VERIFIED]:
   - a single burned-in caption word in 69% of samples;
   - a `DAY N · time · temperature` HUD stamp at chapter openings;
   - big "DAY N" title cards with the number in red (#C0433C [MEASURED]).
6. **Credibility devices** [VERIFIED]:
   - historical "this really happened" cutaways: the castaway Selkirk, a 1924 White House scene, Norse Greenland, the 1942 planes in the ice;
   - a description section called **"What's real and what isn't"**;
   - a safety disclaimer.

## 2. Structure (chapter map) [VERIFIED from video metadata]

| Act | Time | Chapters | Narrative job |
|---|---|---|---|
| Cold open | 0:00–0:42 | "Part 1 · They're gone" | A specific time, place and crowd, then everyone vanishes. Second person: "You blink." |
| Act 1: survival basics | 0:42–5:54 | Day 1 Street → Last Lights → Stars → Water → Tunnels → Smell → Pack | One system fails per chapter: power, water pressure, subway pumps, food spoilage, feral dogs |
| Act 1b: isolation | 5:54–10:25 | Day 50 Quiet → 70 Green → 100 Last Voice → 160 Fire → 280 Cold → 302 Scratch | Psychology, nature returns, injury risk (antibiotics), a historical analogue (Selkirk) |
| Midpoint hook | 10:25–11:15 | Day 365 · The Sky | A contrail: **someone else is alive** |
| Act 2 | 11:15–23:41 | Part 2: Day 366–730 | A second character (Ruth, pilot), logistics: fuel, seed banks, radio. Ends with a plan: fly the Atlantic |
| Act 3 | 23:41–36:06 | Part 3: Day 731–1000 | The journey: icing, Greenland, Iceland, Svalbard. A community of nine. The mystery of the jet is solved |
| Resolution | 36:06–37:12 | Day 1095 · The Sun | Polar sunrise; the group on the stairs |

- **Rhythm:** chapter length runs 31–75 s [VERIFIED]. The day gaps grow as the story moves on (1, 2, 3, 5, 12, 21, 50, 70, 100…), which compresses time while keeping it concrete.
- **Callbacks** [VERIFIED]:
  - The day-1 street returns at 24:18.
  - The empty subway car returns at 11:14, on Day 366.
  - The rooftop is the emotional "home base".
- **Engagement prompt** [VERIFIED/INFERRED]:
  - The description asks "Which day would have broken you first? Tell me in the comments."
  - The caption word "COMMENTS" appears at 23:28, the end of Part 2 [VERIFIED]. This suggests a spoken mid-video comment prompt [INFERRED].

## 3. Frame-type mix [VERIFIED counts from 225 samples]

| Frame type | Share | Description |
|---|---|---|
| Character in plate | 28% | Wide shots: characters small (5–20% of frame height) inside a detailed environment |
| Plate only | 23% | Establishing or atmosphere, no characters |
| Infographic, dark | 15% | Flat vector graphics on near-black navy (#0D1019 [MEASURED]) |
| Character close-up | 8% | Head and shoulders, background heavily defocused |
| Map / globe | 7% | Flat maps: dark ocean, muted land, white labels |
| Graphic over blurred plate | 5% | A flat object (thermometer, pot, checklist card) floating over the defocused location |
| Infographic, light | 4% | Cream or paper backgrounds: fridge contents, tank cross-sections |
| Title card | 4% | "DAY N" in white, number in red, small subtitle, over a plate |
| POV hands | 3% | The hero's mustard sleeve and black mitten handling objects |
| Insert | 3% | Object close-ups: a gauge, a fireplace |

**Shot sizes:**

| Shot | Share |
|---|---|
| Wide | 48% |
| Graphic | 31% |
| Close-up | 13% |
| Medium | 5% |
| Aerial | 2% |

The video is dominated by wide shots: the world is the star and the hero is small inside it.

**Measured contrast between shot types:**
- Close-ups have an edge density of 0.083, against 0.24–0.28 for wide plates. Close-up backgrounds are strongly blurred to isolate the face.
- Dark infographics have a mean luma of 0.15, against 0.37–0.40 for plates. Graphics read as "night cards" that rest the eye between busy plates.

## 4. Visual production breakdown

These are summaries. The detail is in `visual_style_bible.md`, `camera_and_lighting_notes.md` and `motion_notes.md`.

- **Characters** [VERIFIED]
  - The hero is "Hardy":
    - a large plain white circular head with two dot eyes and a small line or "o" mouth;
    - no nose or ears;
    - a mustard-yellow puffer jacket and a red scarf;
    - black mitten hands.
  - Companion: Bagel, a tan beagle-type dog with a blue collar. He is more detailed and shaded than the humans.
  - Other humans share the round head but get hair, glasses, hats and coat colours: Ruth's grey bun, glasses and headset; Olena; Pavel; Signe.
  - New characters are introduced with a **luggage-tag name label** [VERIFIED].
- **Environments** [VERIFIED]
  - Painterly, high-detail plates in a warm "storybook realism" style. Recurring locations are re-rendered for each season and condition.
  - Detail is dense: fire escapes, signage, litter, foliage. Abandonment is shown with open car doors, weeds, rust and snow.
- **Lighting** [VERIFIED]
  - Strong time-of-day moods: sunrise orange, golden hour, blue-hour night, storm, polar night with aurora, midnight sun.
  - Practical lights (street lamps, fire barrels, candles) give warm pools against cool ambient light. See `camera_and_lighting_notes.md`.
- **Graphics** [VERIFIED]
  - Flat, clean, sparse:
    - one idea per card;
    - big numerals in red or amber;
    - white labels;
    - simple pictograms: stick figures, planes, thermometers.
- **Typography** [VERIFIED]
  - Captions are a bold, condensed, all-caps sans-serif, white with a dark outline, centred low in the frame.
  - Title cards use a heavy geometric sans-serif.
- **Not 3D** [VERIFIED]. If our channel goes 3D, it would be **differentiating** from this reference, not copying it.

## 5. What to copy, adapt or avoid

| Technique | Verdict | How we use it (original execution) |
|---|---|---|
| Recurring location that evolves over time | **Adopt (core)** | One "observation plate" per episode, e.g. a meadow, pond or farm, shown at Hour 1 / Week 1 / Year 1 / Year 10 as the missing species' effects build up |
| Day/time HUD stamp | Adapt | Our own stamp, e.g. `T+3 WEEKS · Kenya · 28°C`, in our typeface and colours |
| One-problem-per-chapter with day stamps | **Adopt** | A chapter per consequence, with timestamped chapters in the description |
| Second-person narration | Consider | "You walk outside the morning after the last mosquito died…" Strong immersion, but keep the documentary authority |
| Flat infographic cards between plates | Adopt | Our own palette and icon set; one fact per card |
| Historical "this really happened" cutaway | **Adopt** | Real ecological precedents, e.g. India's vulture collapse, Yellowstone wolves, Australia's dung beetles |
| "What's real and what isn't" in the description | **Adopt** | Fits a science channel even better than it fits fiction |
| Single-word burned-in captions | Test | Good for silent autoplay; ours should use 2–4-word phrases so they read as captions, not noise |
| Round white-head hero, mustard jacket, red scarf, beagle | **Avoid** | Our mascot Pip already differs (bucket hat, round glasses, olive vest). Keep it that way |
| Their "DAY 1 / DAY 365" split thumbnail | **Avoid as-is** | Use a WITH / WITHOUT or YEAR 0 / YEAR 10 comparison with a different divider and layout |

## 6. Gaps

| Item | Status |
|---|---|
| Motion, camera moves, transitions, cut frequency | Not observed (no video) |
| Narration voice, pace (words per minute), music, sound design | Not observed |
| Exact script wording | Not available: no captions or transcript are published for this video |
| Native resolution and colour detail | Only 320×180 previews were inspected |
| Every frame | **Not** inspected: one sample per 9.92 s |

**Next step:** if you upload the MP4, run:

```
ffmpeg scene detection → per-cut timeline → 2–5 fps sampling around motion → fill in motion_notes.md
```
