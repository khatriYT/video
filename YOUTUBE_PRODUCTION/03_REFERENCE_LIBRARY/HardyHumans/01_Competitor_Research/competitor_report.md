# Competitor Research Report: Hardy Humans

- **Researched:** 2026-11-26
- **Channel:** [Hardy Humans](https://www.youtube.com/@HardyHumans), channel ID `UCxBUAJj39JCIQrkjWF--YcQ`
- **Reference video you supplied:** [What If You Were the Last Human on Earth for 3 Years? (Full Story)](https://youtu.be/wqMaepNXeBc). The deep frame analysis is in `../02_Reference_Analysis/report.md`.
- **Raw data:** `channel_videos.csv`, one row per video, snapshot taken 2026-11-26.
  - Rebuild it with `python3 tools/fetch_reference_frames.py <video> <channel> <out>`.

> **Tags used**
> - **[VERIFIED]:** read from public YouTube data: the channel page, video metadata, thumbnails and storyboard frames.
> - **[ANALYSIS]:** my interpretation.
>
> **Limits**
> - No private analytics (CTR, retention, traffic sources, demographics) are available, and none are claimed.
> - The videos themselves could not be played or transcribed here. Script notes therefore come from chapters, descriptions and on-screen caption words.

---

## 1. Key findings

1. **A new channel in breakout.** [VERIFIED]
   - 2,870 subscribers, 23 videos, all uploaded between 2026-10-31 and 2026-11-25: about 0.9 per day.
   - 767K total views. The **median video has 4,586 views**.
   - Three videos hold 81% of all views:
     - the **Full Story** compilation: 320.8K in 5 days;
     - a **GTA 5 tribute**: 194K in 12 days;
     - **"What If Earth Stopped Spinning for One Year?"**: 106K in 11 days.
2. **The compilation outperformed its own parts by about 12×.** [VERIFIED numbers; ANALYSIS interpretation]
   - The three parts it stitches together got 26.3K, 12.3K and 10.7K after 14–20 days. The 37-minute Full Story got 320.8K in 5 days.
   - Parts 4 and 5, uploaded *after* the Full Story, reached 25–27K in 3–4 days, much faster than Parts 2–3 did.
   - Likely reading: the long cut got recommended widely (it is long, chaptered and bingeable), then fed viewers into the series.
3. **"What if" + "Day 1 to Day N" is the house format.** [VERIFIED]
   - 8 of 23 titles include "Day 1 to Day …" or a day range. Most videos are 10–16 min with 8–15 "Day X · The Y" chapters.
   - The format alone does not guarantee success: Rain (4.8K), Magnetic field (4.6K), Apophis (8.5K) and Power out (3.6K) [VERIFIED].
   - **Topic** decides the outlier: a "last human / everyone vanished" premise, and "Earth stopped spinning" [ANALYSIS].
4. **Titles are being A/B tested.** [VERIFIED]
   - Different endpoints returned different titles for the same video within about an hour.
   - Video `A2Id8qtKuK0` showed three titles:
     - "…Part 5: Day 1461 to Day 1825"
     - "What If the Last Humans on Earth Were Waiting at the End of the World?"
     - "What If You Flew to the End of the World to Find the Last 31 Humans?"
   - Video `-MpXD3UnMQg` showed two titles.
   - This is consistent with YouTube's title-testing feature.
5. **Packaging and in-video art are different styles.** [VERIFIED]
   - Thumbnails are bold cel-shaded cartoons with thick black outlines and saturated colour.
   - The video uses painterly plates with flat characters.
   - The thumbnail is built to win the click, not to match the video's look.

## 2. Channel positioning [VERIFIED description + ANALYSIS]

| Item | Finding |
|---|---|
| Stated promise | "Could YOU survive it?" Animated survival stories in the **second person**: "you make the choices, Hardy lives them, and real facts decide whether you make it." |
| Claimed rigour | "Every story is built on real data from historians, scientific studies and agencies like the CDC and FEMA, with sources in each video description." |
| Niche | Hypothetical and historical survival scenarios: apocalypse, planetary disasters, history, extreme jobs. Two off-niche GTA 5 videos ride a gaming trend |
| Audience [ANALYSIS] | Teens to young adults who like "what if" and survival content. Overlaps with animated-explainer audiences |
| Recognisable by | One recurring hero (round white head, mustard jacket, red scarf) and a beagle companion; day-stamped chapters; DAY 1 / DAY N split thumbnails |
| Category | Education [VERIFIED] |

## 3. Performance table [VERIFIED, snapshot 2026-11-26; "per day" is views divided by days since upload]

| Upload | Title (watch page) | Views | Views/day | Like rate | Length |
|---|---|---|---|---|---|
| 10-31 | 1 Year in a Nuclear Bunker. It's Not the Radiation. | 3,609 | 139 | 0.47% | 11:04 |
| 10-31 | What If the Power Went Out for 30 Days in Winter? | 3,556 | 137 | 0.67% | 10:17 |
| 11-01 | 14 Months in a Plague Village. It Wasn't the Rats. (Part 1) | 921 | 37 | 0.65% | 9:55 |
| 11-02 | 14 Months in a Plague Village… (Part 2) | 586 | 24 | 0.85% | 9:50 |
| 11-02 | Zombie Outbreak: 8 Months in Antarctica. It Isn't the Dead. | 1,799 | 75 | 0.50% | 11:52 |
| 11-03 | Zombie Outbreak: 7 Days Left and Only YOU Saw the Group Chat | 2,504 | 109 | 0.40% | 9:28 |
| 11-03 | The Sun Disappeared: Day 1 to Day 30 (Part 1) | 1,655 | 72 | 1.45% | 13:33 |
| 11-06 | **What If You Were the Last Human on Earth? Day 1 to Day 365** | 26,316 | 1,316 | 0.45% | 11:28 |
| 11-08 | What If It Rained for 1 Year? Day 1 to Day 365 | 4,846 | 269 | 0.72% | 13:17 |
| 11-08 | Last Human on Earth? Part 2: Day 366 to Day 730 | 12,277 | 682 | n/a | 12:35 |
| 11-09 | What If You Could Turn Invisible at Will? | 1,089 | 64 | 1.19% | 7:21 |
| 11-12 | Last Human on Earth? Part 3: Day 731 to Day 1095 | 10,664 | 762 | 0.54% | 13:28 |
| 11-13 | How Long Would You Survive in Every Prehistoric Era? | 2,878 | 221 | 0.66% | 16:01 |
| 11-14 | **GTA 5 Characters Saying Goodbye to You Before GTA 6** | 194,092 | 16,174 | 1.62% | 13:01 |
| 11-15 | **What If Earth Stopped Spinning for One Year? (Day 1 to Day 365)** | 105,969 | 9,634 | 0.55% | 13:01 |
| 11-16 | What Did Ancient Humans Actually Do All Day? | 1,194 | 119 | 1.34% | 12:52 |
| 11-19 | GTA 5's Last Ride: One Player Got Left Behind | 6,081 | 869 | n/a | 11:55 |
| 11-20 | What If Earth's Magnetic Field Flipped This Year? (Day 1 to Day 365) | 4,586 | 764 | n/a | 13:49 |
| 11-21 | **What If You Were the Last Human on Earth for 3 Years? (Full Story)** | 320,804 | 64,161 | 0.55% | 37:12 |
| 11-21 | What If Apophis Hit Earth on Friday the 13th? (Day 1 to Day 365) | 8,532 | 1,706 | 0.60% | 13:55 |
| 11-22 | Last Human on Earth and a Baby Was Born? (Part 4) | 25,237 | 6,309 | 0.86% | 14:19 |
| 11-23 | Last Human on Earth? Part 5: Day 1461 to Day 1825 | 27,531 | 9,177 | 0.88% | 13:59 |
| 11-25 | What If You Woke Up 1 Year in the Future Every Morning? (Day 1 to Day 100) | 295 | 295 | 3.39% | 15:59 |

"n/a" means the like or comment count was not exposed in the data read.

### Reading the numbers [ANALYSIS]

**Raw views mislead here.**
- The channel is only 26 days old. Recent videos are only days old.
- Its subscriber base (2,870) is tiny next to its outliers, so almost all views come from recommendations, not subscribers.

**Like rates are low on the outliers (0.55%).**
- This is typical of broad recommendation traffic: many casual viewers watch, few engage.
- The GTA tribute's 1.62% reflects an emotionally invested fandom.

**Upward trend.**
- Since 11-14, every non-GTA upload except the newest has topped 4.5K, against 0.6–3.6K in the channel's first week.
- The channel's baseline is rising.

## 4. Topic patterns [ANALYSIS]

| Pattern | Examples | Outcome |
|---|---|---|
| Everyone vanished / last human | Last Human series | Strongest franchise (Parts 1–5 plus Full Story) |
| Planet-scale physics "what if" | Earth stopped spinning; magnetic field flip; Apophis; Sun disappeared | One big hit (spinning), the rest modest |
| Survive-a-place | Nuclear bunker, Antarctica, plague village | Low (0.6–3.6K) |
| Gaming nostalgia | GTA 5 tribute | A hit, but off-brand |
| Historical daily life | Ancient humans, prehistoric eras | Low |

**Takeaway for us:** large-scale, simple-to-grasp premises with a **visible world transformation** beat confined-location survival. An ecology "what if X disappeared" is exactly a world-transformation premise.

## 5. Title patterns [VERIFIED from 23 titles; ANALYSIS of what works]

| Pattern | Share | Examples |
|---|---|---|
| Starts with "What If…" | 61% (14/23) | "What If Earth Stopped Spinning for One Year?" |
| Explicit time span ("Day 1 to Day 365", "1 Year", "30 Days", "14 Months") | 70% | "…(Day 1 to Day 365)" |
| Second person ("You") | 35% | "What If You Were the Last Human on Earth?" |
| Twist suffix ("It's Not the Radiation.", "It Wasn't the Rats.") | 17% | All low performers, interestingly |
| Part / series tags | 26% | "(Part 4)", "Part 2: Day 366 to Day 730" |

- **Length:** 45–80 characters.
- **Tone:** sentence case with a question mark. No caps-lock words, no emoji.

## 6. Thumbnail patterns [VERIFIED from 23 maxres thumbnails]

- **Hero face large:** 35–50% of frame height, on the left or right. Expressions: worry, "o"-mouth shock, a sweat drop, tears.
- **The DAY split:** "DAY 1 | DAY 365" diagonal split showing before and after, with the second number in red. Used on 8 of 23, including the whole Last Human series.
- **Text:**
  - 2–4 words in a heavy condensed sans-serif (white with a black outline, one word in red or yellow): "8 BILLION GONE", "THE FIRST BABY", "NO SHIELD", "IT HITS HERE".
- **Art:** thick black outlines, cel shading, very saturated warm/cool contrast (orange sunset against blue).
  - This is cleaner and bolder than the in-video art.
- **Companion:** the dog appears in every Last Human thumbnail.
- **The reference video's thumbnail:** hero and dog large on the left, and an empty NYC street with abandoned taxis, bags and a stroller receding to a sunset.
  - Text: "8 BILLION" (white) / "GONE" (red).

## 7. Script and storytelling [VERIFIED from the description, 44 chapters and caption words; ANALYSIS]

**Hook (0:00–0:42)**
- Hyper-specific, ordinary moment: "It's 8:14 on a Tuesday morning in March. You're on the downtown train in New York, half asleep, with forty people around you."
- One-beat event: "You blink. And they're gone."
- Immediate scale: "More than eight billion people just disappeared. Everyone except you." [VERIFIED, description]

**Structure**
- Day-stamped chapters. Each poses **one concrete problem** with **one real mechanism**:
  - water pressure only reaches about 6 floors;
  - subway pumps move about 13 million gallons a day;
  - the 2003 blackout.
- The day gaps widen as the story goes on.
- The midpoint twist (Day 365: a contrail) changes the goal from *survive* to *find them*.

**Credibility**
- Historical analogues give each speculative beat a real precedent:
  - Alexander Selkirk;
  - the 1942 aircraft dug out of 268 ft of Greenland ice;
  - Norse Greenland.
- The description ends with **"WHAT'S REAL AND WHAT ISN'T"** and a safety disclaimer.

**Retention devices** [ANALYSIS]
- A day counter that always increases.
- A companion animal in jeopardy.
- Open questions planted early and paid off late ("who was flying that jet").
- Callbacks to home-base locations.
- A comment prompt near the end of Part 2.

**Ending**
- An emotional image: the community watching the sun return after polar night.
- A comment question in the description.

**Not observed:** exact narration wording, voice, pace and music (no transcript or audio available).

## 8. Visual production [summary; full detail in ../02_Reference_Analysis/]

- **Approach:** a 2D hybrid, **not 3D**:
  - flat vector characters;
  - painterly AI-style background plates [INFERRED];
  - flat infographic cards;
  - word-by-word captions.
- **Strongest techniques:**
  1. evolving recurring locations;
  2. heavy background defocus for close-ups and graphics;
  3. one fact per graphic card;
  4. time-of-day lighting moods;
  5. historical cutaways in the same art style.

## 9. Opportunities the competitor has not explored [ANALYSIS]

1. **Ecology and biodiversity "what ifs."**
   - Their "what ifs" are human-centred: people, planets, disasters.
   - None of the 23 is about a species, an ecosystem or a food web.
   - That is our niche, and it is open on this channel.
2. **A visibly changing *living* world.**
   - Their recurring plates mostly show decay of human infrastructure.
   - We can show **ecosystem cascades** at one fixed spot: flowers that stop being pollinated, a pond that changes, birds that disappear.
3. **Real 3D for consistency.**
   - Their AI plates drift between versions.
   - A real 3D environment rendered from fixed cameras gives exact continuity across "Hour 1 → Year 10".
4. **Real-precedent case studies are the norm in ecology**, and they are stronger than fiction:
   - India's vulture collapse;
   - Yellowstone wolves;
   - Australia's dung beetles;
   - the American chestnut.
5. **"What's real and what isn't."** They do it for fiction. For science we can go further: on-screen "EVIDENCE: strong / debated / speculative" tags.
6. **Long-form compilations.** Their 37-min cut was the breakout. We already have 2 × 12-min episodes. A compilation, e.g. "What If the Smallest Animals Disappeared? (Full Series)", is cheap to test once 3–4 episodes exist.

## 10. Practical recommendations for an original channel [ANALYSIS]

1. Keep **"What If [Creature] Disappeared?"** titles. Test a time-span variant ("…(Hour 1 to Year 10)") and a "You" framing in packaging tests.
2. Build every episode on a **day-stamped consequence ladder**: one consequence per chapter, 40–70 s each, with chapters in the description.
3. Use **one recurring observation plate** per episode, the same camera at every time stamp. It becomes the episode's visual spine and the thumbnail's before/after.
4. **Anchor every speculative beat to a real precedent or study.** Close the description with "What's real and what isn't" and a source list.
5. Package with a **large expressive mascot face plus the creature (or its absence)** and 2–4 words of text. Do **not** reuse their diagonal DAY split. Use our own WITH / WITHOUT comparison device instead.
6. Plan a **compilation** once 3 episodes exist.
7. Stay on-niche. Their GTA hit does not transfer to a science brand.

## Sources

- Channel page and video list: https://www.youtube.com/@HardyHumans/videos (read via yt-dlp, 2026-11-26)
- Per-video metadata: https://youtu.be/{id} for each row in `channel_videos.csv`
- Reference video: https://youtu.be/wqMaepNXeBc, including its description's "What's real and what isn't" section
- Thumbnails: `https://i.ytimg.com/vi/{id}/maxresdefault.jpg` (local copies, gitignored)
